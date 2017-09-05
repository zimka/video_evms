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

    
 В этом же файле нужно заменить импорт edxval.api на импорт video_evms.api


 ::

    try:
        #import edxval.api as edxval_api
        import video_evms.api as edxval_api 
    except ImportError:
        edxval_api = None

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

* Запустить команду для замены статики

  ::

    ./manage.py lms video_quality enable --settings=npoed


* Добавить FEATURE["EVMS_QUALITY_CONTROL_ON"] в настройки

* Пересобрать статику

 ::


   paver update_assets lms --settings=npoed
