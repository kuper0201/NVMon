[English version](https://github.com/kuper0201/NVMon/README_eng.md)

# NVMon
![Python](https://img.shields.io/badge/Python3-3776AB?style=for-the-badge&logo=Python&logoColor=white)

> NVIDIA-SMI를 이용해 GPU 상태를 모니터링하기 위한 도구입니다.

## Preview

<table>
    <tbody>
        <tr>
            <th>Icon ver</th>
            <th><img src="images/icon_ver.png" width="600"/></th>
        </tr>
        <tr>
            <td>Text ver</td>
            <td><img src="images/text_ver.png" width="600"/></td>
        </tr>
    </tbody>
</table>

## Table of Units
|Item|Description|Unit|Example of output|
|---|---|---|---|
|Name|GPU 이름|String|NVIDIA P102-100|
|Usg|GPU 사용량|Percentage|98%|
|Tmp|GPU 온도|Degree|73°C|
|VRAM|GPU 메모리 상태|GigaByte and Percentage|9.4G / 10G(94%)|
|FAN|팬 속도|Percentage|82%|
|PWR|전원 상태|Watt|210.00W / 250.00W|

## Features
- 모니터링 창은 다른 창에 가려지지 않음
- 적은 화면 차지
- 크로스 플랫폼 지원(리눅스, Windows10에서 테스트 됨)

## How to install
1. NVIDIA-SMI가 필요하므로 NVIDIA 드라이버를 설치해야 합니다. (NVIDIA-SMI는 NVIDIA 드라이버에 포함되어 있음)
2. [Release Page](https://github.com/kuper0201/NVMon/releases)에서 실행 파일을 다운로드합니다.
3. 다운로드 된 파일을 압축 해제 후 실행합니다.

## Change Log
- ver1.1 (2024/7/16)
    - 이제 텍스트 대신 아이콘으로 상태 아이템을 표시합니다.
    
- ver1.0 (2024/1/5)
    - First Release

## To do
- 다중 GPU 지원 추가
