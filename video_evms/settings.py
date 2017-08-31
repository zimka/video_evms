import os
from django.conf import settings

VIDEO_STATUSES = ('uploading', 'new', 'storage', 'compressor')
MESSAGES = {
    "ERROR_MESSAGE": u"*************************Error*************************",
    "PROGRESS_MESSAGE": u"+++++++++++++++In progress++++++++++++++",
    "MANUALLY_MESSAGE": u"***Evms video id is None or inputted manually***",
    "NONE_MESSAGE":"None"
}

if hasattr(settings, "EVMS_VIDEO_STATUSES"):
    VIDEO_STATUSES = settings.EVMS_VIDEO_STATUSES


ORIGINAL_JS_DIR = "/edx/app/edxapp/edx-platform/common/lib/xmodule/xmodule/js/src/video/"
ORIGINAL_JS_FILES = ("02_html5_video.js", "05_video_quality_control.js")
SAVED_ORIGINAL_JS_FILES = tuple("." + x for x in ORIGINAL_JS_FILES)

NEW_JS_FILES = ('02_html5_video.js',
                '05_video_quality_control.js',
                '019_html5_video.js',
                '049_video_quality_control.js'
                )


def is_quality_control_set_up():
    js_video_files = os.listdir(ORIGINAL_JS_DIR)
    return all(x in js_video_files for x in SAVED_ORIGINAL_JS_FILES) \
                        and all(x in js_video_files for x in NEW_JS_FILES)
