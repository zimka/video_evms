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

* Установить пакет
* В common/lib/xmodule/xmodule/video_module/video_module.py из video_evms.mixins импортировать VideoModuleEvmsMixin, VideoDescriptorEvmsMixin, добавить их к VideoModule и VideoDescriptor соответственно
* В common/lib/xmodule/xmodule/course_module.py из video_evms.mixins импортировать CourseModuleEvmsMixin, добавить ее к CourseModule
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


* Добавить в env.py переменные EVMS_URL, EVMS_API_KEY; добавить "video_evms" в INSTALLED_APPS