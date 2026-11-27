BUILD_DIR ?= build

.PHONY: all iso clean

all: iso

iso:
	cmake -S . -B "$(BUILD_DIR)" -DCMAKE_TOOLCHAIN_FILE="$${PSN00BSDK_LIBS}/cmake/sdk.cmake"
	cmake --build "$(BUILD_DIR)" --target iso

clean:
	rm -rf "$(BUILD_DIR)"
