Содержание
==========

* `Описание`_.
* `Установка`_.

Описание
========

Пакет добавляет два дополнения к видео-плееру edx:

1. Список доступных видео для курса в редакторе Studio

2. Переключение между потоками видео разного разрешения

Установка
=========


Для установки дополнения 1:
---------------------------


* Установить пакет
* В common/lib/xmodule/xmodule/video_module/video_module.py из video_evms.mixins импортировать VideoModuleEvmsMixin, VideoDescriptorEvmsMixin, добавить их к VideoModule и VideoDescriptor соответственно


  ::

    class VideoModule(VideoModuleEvmsMixin, VideoFields, ...)
    ...
    class VideoDescriptor(VideoDescriptorEvmsMixin, VideoFields,...)


* в lms/templates/video.html найти и добавить:


  ::

    <div class="video-player">
        <div id="${id}"></div>
          <h4 class="hd hd-4 video-error is-hidden">${_('No playable video sources found.')}</h4>
    -----------ДОБАВИТЬ-----------
          % if only_original:
            <h4 class="hd hd-4 video-error">${_('Video compression in progress. Until the end of compression it won't be visible for students.')}</h4>
          % endif
    ------------------------------
    </div>
    <div class="video-player-post"></div>


* Добавить в env.py переменные EVMS_URL, EVMS_API_KEY, FEATURES["EVMS_TURN_ON"]; добавить "video_evms" в INSTALLED_APPS; если статусы видео отличаются от ('uploading', 'new', 'storage', 'compressor'), их мжно перезаписать в переменной EVMS_VIDEO_STATUSES

Для установки дополнения 2:
---------------------------

* Установить дополнение 1

* В файле common/lib/xmodule/xmodule/js/src/video/02_html_video.js заменить

  ::

    define(
    'video/02_html5_video.js', // Заменить на: 'video/019_html5_video.js',
    [],


  и переименовать файл в 019_html5_video.js

* В файле common/lib/xmodule/xmodule/js/src/video/05_video_quality_control.js заменить

  ::

    define(
    'video/05_video_quality_control.js', // Заменить на: 'video/049_video_quality_control.js',
    [],


  и переименовать файл в 049_video_quality_control.js

* Кинуть video_evms/static/02_html5_video.js и video_evms/static/05_video_quality_control.js в папку common/lib/xmodule/xmodule/js/src/video/

* В файле common/lib/xmodule/xmodule/video/video_module.py в классе VideoModule найти поле js:

 ::

    class VideoModule(...):
    ...
    js = {
        'js': [
            resource_string(module, 'js/src/time.js'),
            resource_string(module, 'js/src/video/00_component.js'),
            resource_string(module, 'js/src/video/00_video_storage.js'),
            resource_string(module, 'js/src/video/00_resizer.js'),
            ...
            ]
          }

 Добавить в конце списка

 ::


            ...
            resource_string(module, 'js/src/video/019_html5_video.js'),
            resource_string(module, 'js/src/video/049_video_quality_control.js'),
            ]
          }
