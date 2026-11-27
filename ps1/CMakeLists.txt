cmake_minimum_required(VERSION 3.21)

include("$ENV{PSN00BSDK_LIBS}/cmake/sdk.cmake")

project(
    kintoki
    LANGUAGES C
    VERSION 0.1.0
    DESCRIPTION "Kintoki PS1 dance showcase placeholder"
)

file(WRITE "${PROJECT_BINARY_DIR}/system.cnf"
    "BOOT=cdrom:\\KINTOKI.EXE;1\n"
    "TCB=4\n"
    "EVENT=10\n"
    "STACK=801FFF00\n"
)

configure_file(iso.xml.in iso.xml @ONLY)

psn00bsdk_add_executable(kintoki GPREL main.c)
psn00bsdk_add_cd_image(
    kintoki_iso
    kintoki
    iso.xml
    DEPENDS kintoki "${PROJECT_BINARY_DIR}/system.cnf"
)

add_custom_target(iso ALL DEPENDS kintoki_iso)
