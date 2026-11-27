#include <stdint.h>
#include <psxgpu.h>

#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 240
#define OT_LENGTH 8
#define BUFFER_LENGTH 2048

typedef struct {
    DISPENV display;
    DRAWENV draw;
    uint32_t ordering_table[OT_LENGTH];
    uint8_t primitives[BUFFER_LENGTH];
} RenderBuffer;

static RenderBuffer buffers[2];
static int active_buffer;
static uint8_t *next_primitive;

static void setup_video(void) {
    SetDefDrawEnv(&buffers[0].draw, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
    SetDefDispEnv(&buffers[0].display, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
    SetDefDrawEnv(&buffers[1].draw, 0, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT);
    SetDefDispEnv(&buffers[1].display, 0, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT);

    setRGB0(&buffers[0].draw, 8, 5, 16);
    setRGB0(&buffers[1].draw, 8, 5, 16);
    buffers[0].draw.isbg = 1;
    buffers[1].draw.isbg = 1;

    active_buffer = 0;
    next_primitive = buffers[0].primitives;
    ClearOTagR(buffers[0].ordering_table, OT_LENGTH);
    SetDispMask(1);
}

static void *new_primitive(int depth, uint32_t size) {
    RenderBuffer *buffer = &buffers[active_buffer];
    void *primitive = next_primitive;
    addPrim(&buffer->ordering_table[depth], primitive);
    next_primitive += size;
    return primitive;
}

static void present(void) {
    RenderBuffer *draw_buffer = &buffers[active_buffer];
    RenderBuffer *display_buffer = &buffers[active_buffer ^ 1];

    DrawSync(0);
    VSync(0);
    PutDispEnv(&display_buffer->display);
    DrawOTagEnv(&draw_buffer->ordering_table[OT_LENGTH - 1], &draw_buffer->draw);

    active_buffer ^= 1;
    next_primitive = buffers[active_buffer].primitives;
    ClearOTagR(buffers[active_buffer].ordering_table, OT_LENGTH);
}

int main(void) {
    int frame = 0;

    ResetGraph(0);
    setup_video();

    for (;;) {
        int sway = (frame & 31) - 16;
        TILE *body = new_primitive(2, sizeof(TILE));
        TILE *head = new_primitive(1, sizeof(TILE));
        TILE *accent = new_primitive(0, sizeof(TILE));

        setTile(body);
        setXY0(body, 128 + sway / 2, 92);
        setWH(body, 64, 92);
        setRGB0(body, 20, 24, 36);

        setTile(head);
        setXY0(head, 140 + sway, 54);
        setWH(head, 40, 32);
        setRGB0(head, 236, 184, 52);

        setTile(accent);
        setXY0(accent, 116 - sway, 190);
        setWH(accent, 88, 8);
        setRGB0(accent, 236, 184, 52);

        present();
        ++frame;
    }
}
