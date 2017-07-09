# -*- coding: utf-8 -*-
import logging
from django.conf import settings
from xblock.fields import Scope, String
from xmodule.modulestore.inheritance import own_metadata

import api as edxval_api

try:
    from branding.models import BrandingInfoConfig
    from xmodule.video_module.video_utils import create_youtube_string, get_poster, rewrite_video_url
    from xmodule.video_module.bumper_utils import bumperize
except:  # заглушки для импорта из shell
    BrandingInfoConfig = None
    dummy = lambda x: None
    bumperize = dummy
    create_youtube_string = dummy
    rewrite_video_url = dummy
    get_poster = dummy

log = logging.getLogger(__name__)
_ = lambda text: text
MESSAGES = {
    "ERROR_MESSAGE": u"*************************Error*************************",
    "PROGRESS_MESSAGE": u"+++++++++++++++In progress++++++++++++++",
    "MANUALLY_MESSAGE": u"***Evms video id is None or inputted manually***",
    "NONE_MESSAGE":"None"
}
VIDEO_STATUSES = ('uploading', 'new', 'storage', 'compressor')
if hasattr(settings, "EVMS_VIDEO_STATUSES"):
    VIDEO_STATUSES = settings.EVMS_VIDEO_STATUSES


class _VideoModuleEvmsMixin(object):
    """
    Этот класс надо наследовать в xmodule.video_module.video_module.VideoModule.
    Он перезаписывает метод render_template у наследника, добавляя в контекст
    поле only_original: если видео на EVMS доступно только в несжатом виде, то
    преподавателю оно показывается с сообщением об этом.
    """
    def __init__(self, *args, **kwargs):
        super(_VideoModuleEvmsMixin, self).__init__(*args, **kwargs)
        #TODO: найти лучший вариант проверки
        is_studio = len(self.runtime.STATIC_URL.split('/static/')[1]) > 1
        only_original = False
        if is_studio:
            available_profiles = edxval_api.get_available_profiles(self.edx_video_id, None)
            if len(available_profiles) == 1 and u'original' in available_profiles:
                only_original = True
        self.child_render_template = self.system.render_template

        def updated_context_render_template(name, context):
            context['only_original'] = only_original
            return self.child_render_template(name, context)

        self.system.render_template = updated_context_render_template


class _VideoDescriptorEvmsMixin(object):
    """
    Этот класс надо наследовать в xmodule.video_module.video_module.VideoDescriptor
    Он перезаписывает методы editr_saved и get_context у наследника: синхронизирует
    поле выпадающего списка и edx_video_id, подменяет второе на первое при рендере.
    """
    edx_dropdown_video_id = String(
        help=_(
            "List of known Video IDs for this course. Updates automatically. "
            "To set Video ID from other course go to 'Advanced' and use 'Video ID'"),
        display_name=_(" Course Video ID"),
        scope=Scope.settings,
        default="",
    )

    def __init__(self, *args, **kwargs):
        super(_VideoDescriptorEvmsMixin, self).__init__(*args, **kwargs)
        if self.edx_video_id != self.edx_dropdown_video_id:
            self.edx_dropdown_video_id = self.edx_video_id

        self.child_get_context = self.get_context
        self.get_context = self.updated_get_context

        self.child_editor_saved = self.editor_saved
        self.editor_saved = self.updated_editor_saved

    def updated_get_context(self):
        """
        Используется потомком вместо get_context
        """
        context = self.child_get_context()
        self.editable_metadata_fields['edx_video_id'] = self.editable_metadata_fields['edx_dropdown_video_id']
        context['transcripts_basic_tab_metadata']['edx_video_id'] = self.editable_metadata_fields[
            'edx_dropdown_video_id']
        return context

    def updated_editor_saved(self, user, old_metadata, old_content):
        """
        Используется потомком вместо editor_saved
        """
        self.child_editor_saved(user, old_metadata, old_content)
        self.runtime.modulestore.update_item(self, user.id)
        self.synch_edx_id(old_metadata=old_metadata, new_metadata=own_metadata(self))
        self.save()

    def studio_view(self, context):
        self.set_video_evms_values()
        return super(_VideoDescriptorEvmsMixin, self).studio_view(context)

    @staticmethod
    def edx_dropdown_video_overriden(s):
        return "'Additional value': {}".format(s)

    def synch_edx_id(self, old_metadata=None, new_metadata=None):
        """
        Согласует данные в полях edx_dropdown_video_id и edx_video_id перед сохранением
        """
        dropdown_eid = self.edx_dropdown_video_id
        native_eid = self.edx_video_id
        if dropdown_eid == native_eid:
            return

        def master_native(eid):
            block = self.fields["edx_dropdown_video_id"]
            if not block.values:
                return
            values = [v["value"] for v in block.values]
            if eid not in values:
                block._values.append({"display_name": self.edx_dropdown_video_overriden(eid), "value": eid})
            self.edx_dropdown_video_id = eid

        def master_dropdown(eid):
            if eid:
                self.edx_video_id = eid
            else:
                self.edx_video_id = ""

        """
        Смотрим какое поле поменял пользователь: это поле будет master
        """
        if not old_metadata and not new_metadata:
            """
            метаданные не передали - считаем edx_dropdown_video_id мастером, т.к. уже есть возможность
            сделать edx_video_id мастером явно, поставив в edx_dropdown_video_id: None
            """
            master_dropdown(dropdown_eid)
            return
        old_native_eid = old_metadata.get('edx_video_id', None)
        new_native_eid = new_metadata.get('edx_video_id', None)
        old_dropdown_eid = old_metadata.get('edx_dropdown_video_id', None)
        new_dropdown_eid = new_metadata.get('edx_dropdown_video_id', None)
        if old_native_eid != new_native_eid and old_dropdown_eid != new_dropdown_eid:
            """Пользователь поменял оба поля. Мастер edx_dropdown_video_id, аргументацию см. выше"""
            master_dropdown(dropdown_eid)
            return
        if old_native_eid != new_native_eid:
            master_native(native_eid)
            return
        if old_dropdown_eid != new_dropdown_eid:
            master_dropdown(new_dropdown_eid)
        return

    def set_video_evms_values(self):
        if edxval_api:
            get_course_edx_val_ids = edxval_api.get_course_edx_val_ids
        else:
            get_course_edx_val_ids = lambda x: [{"display_name": u"None", "value": ""}]
        course = self.runtime.modulestore.get_course(self.location.course_key)
        values = get_course_edx_val_ids(course.id)
        if not values:
            values = [{"display_name": MESSAGES["NONE_MESSAGE"], "value": ""}]
        first_value = [{"display_name": MESSAGES['MANUALLY_MESSAGE'], "value": ""}]

        ok_values = []
        new_values = []
        error_values = []
        override = []
        if self.edx_video_id not in [v["value"] for v in values]:
            override = [
                {"display_name": self.edx_dropdown_video_overriden(self.edx_video_id), "value": self.edx_video_id}]
        for v in values:
            if 'status' in v:
                if v['status'] == 'ok':
                    ok_values.append(v)
                elif v['status'] in VIDEO_STATUSES:
                    new_values.append(v)
                else:
                    log.warning(u"Status of {} is {}".format(v['display_name'], v['status']))
                    error_values.append(v)
        if new_values:
            new_values = [{"display_name": MESSAGES['PROGRESS_MESSAGE'], "value": ""}] + new_values
        if error_values:
            error_values = [{"display_name": MESSAGES['ERROR_MESSAGE'],
                             "value": ""}] + error_values
        values = override + first_value + ok_values + new_values + error_values

        self.fields["edx_dropdown_video_id"]._values = values


"""
Заглушки для отключения фичи
"""
class VideoModuleEvmsMixin(_VideoModuleEvmsMixin): pass
class VideoDescriptorEvmsMixin(_VideoDescriptorEvmsMixin): pass

try:
    if not settings.FEATURES.get("EVMS_TURN_ON"):
        class VideoModuleEvmsMixin(object): pass
        class VideoDescriptorEvmsMixin(object): pass
except:
    pass

