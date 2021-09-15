from typing import List
from dataclasses import dataclass
from datetime import datetime, time

@dataclass(frozen=True, order=True)
class Video:
    __id: str
    __title: str
    __date_added: datetime

    __date_uploaded: datetime
    __uploader: str
    __uploader_id: str
    __duration: time

    def prepare_export(self) -> List[str]:
        url = f'https://www.youtube.com/watch?v={self.__id}'

        package = [
            self.__date_added.strftime('%Y/%m/%d %H:%M:%S'),
            self.__uploader,
            self.__title,
            self.__duration.strftime('%H:%M:%S'),
            url,
            self.__id,
            self.__uploader_id,
            self.__date_uploaded.strftime('%Y/%m/%d %H:%M:%S')
        ]
        return package
