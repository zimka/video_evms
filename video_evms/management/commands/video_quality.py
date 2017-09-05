# coding=utf-8
"""
Подменяет js файлы, добавляя в html5 плеер контроль качества видео.
"""
import pkgutil
import shutil
import os
from io import StringIO
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from video_evms.settings import ORIGINAL_JS_DIR, ORIGINAL_JS_FILES, \
    SAVED_ORIGINAL_JS_FILES, NEW_JS_FILES, is_quality_control_set_up


def get_package_js_file_stream(x):
    return StringIO(unicode(pkgutil.get_data("video_evms", 'static/' + x)))


def get_edx_js_file_stream(x, mode='a+'):
    return open(ORIGINAL_JS_DIR + x, mode)


class Command(BaseCommand):

    args = "<{enable, disable}>"
    help = "Switches static for video_evms feature VIDEO_QUALITY. Example:" \
           "'./manage.py lms video_quality enable'" \
           "./manage.py lms video_quality disable"

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        task = args[0]
        if task == 'enable':
            self.enable_video_quality()
        elif task == 'disable':
            self.disable_video_quality()
        else:
            raise CommandError("Unknown task type: '{}'. Use 'enable' or 'disable'".format(task))

    def enable_video_quality(self):
        # Делаем бэкап файлов edx
        if is_quality_control_set_up():
            raise CommandError("Video quality is enabled already.")

        for original, saved in zip(ORIGINAL_JS_FILES, SAVED_ORIGINAL_JS_FILES):
            f = get_edx_js_file_stream(original)
            g = get_edx_js_file_stream(saved, 'w')
            shutil.copyfileobj(f, g)
            os.remove(ORIGINAL_JS_DIR + original)
        # Копируем файлы из статики пакета в edx
        for name in NEW_JS_FILES:
            f = get_package_js_file_stream(name)
            g = get_edx_js_file_stream(name)
            shutil.copyfileobj(f, g)

        message = "Js files are added successfully."
        missed_features = []
        for f in ("EVMS_TURN_ON", "EVMS_QUALITY_CONTROL_ON"):
            if not settings.FEATURES.get(f, False):
                missed_features.append(f)
        if missed_features:
            message += "You still have to set FEATURE up: " + ",".join(missed_features)
        self.stdout.write(
            message
        )

    def disable_video_quality(self):
        # Проверяем что js-файлы были раньше добавлены
        if not is_quality_control_set_up():
            raise CommandError("Video quality wasn't enabled earlier.")

        for filename in NEW_JS_FILES:
            os.remove(ORIGINAL_JS_DIR + filename)
        for original, saved in zip(ORIGINAL_JS_FILES, SAVED_ORIGINAL_JS_FILES):
            shutil.move(ORIGINAL_JS_DIR + saved,  ORIGINAL_JS_DIR+ original)

        message = "Js files are removed successfully."
        if settings.FEATURES.get("EVMS_QUALITY_CONTROL_ON", False):
            message += "You still have to turn off FEATURE 'EVMS_QUALITY_CONTROL_ON'"
        self.stdout.write(
            message
        )
