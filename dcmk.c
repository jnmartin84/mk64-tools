#include <kos.h>
#include <dc/pvr.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "kartpal.h"

#include "decodes.c"
//void DecodeJaguar(unsigned char *input, unsigned char *output)

pvr_init_params_t pvr_params = {
	{ 0, 0, PVR_BINSIZE_16, 0, 0 },
	1048576,
	0, // 0 is dma disabled
	0, // fsaa
	1, // 1 is autosort disabled
	2, // extra OPBs
	0, // Vertex buffer double-buffering enabled
};

void *all_karts[8][321];
pvr_ptr_t pvr_kart[8];

uint8_t __attribute__((aligned(32))) decodebuf[4096];

#define get_color_argb1555(rrr, ggg, bbb, aaa)                                          \
        ((uint16_t)(((aaa & 1) << 15) | (((rrr >> 3) & 0x1f) << 10) |   \
                    (((ggg >> 3) & 0x1f) << 5) | ((bbb >> 3) & 0x1f)))


void load_all_karts(void) {

	char fn[256];
	for(int i=0;i<=320;i++) {
		sprintf(fn, "/pc/bowser/kart%03d.raw.enc", i);
		ssize_t fnsize = fs_load(fn, &all_karts[0][i]);
//		printf("load %s %d\n", fn, fnsize);
	}
	for(int i=0;i<=320;i++) {
		sprintf(fn, "/pc/donkey/kart%03d.raw.enc", i);
		ssize_t fnsize = fs_load(fn, &all_karts[1][i]);
//		printf("load %s %d\n", fn, fnsize);
	}
	for(int i=0;i<=320;i++) {
		sprintf(fn, "/pc/luigi/kart%03d.raw.enc", i);
		ssize_t fnsize = fs_load(fn, &all_karts[2][i]);
//		printf("load %s %d\n", fn, fnsize);
	}
	for(int i=0;i<=320;i++) {
		sprintf(fn, "/pc/mario/kart%03d.raw.enc", i);
		ssize_t fnsize = fs_load(fn, &all_karts[3][i]);
//		printf("load %s %d\n", fn, fnsize);
	}
	for(int i=0;i<=320;i++) {
		sprintf(fn, "/pc/peach/kart%03d.raw.enc", i);
		ssize_t fnsize = fs_load(fn, &all_karts[4][i]);
//		printf("load %s %d\n", fn, fnsize);
	}
	for(int i=0;i<=320;i++) {
		sprintf(fn, "/pc/toad/kart%03d.raw.enc", i);
		ssize_t fnsize = fs_load(fn, &all_karts[5][i]);
//		printf("load %s %d\n", fn, fnsize);
	}
	for(int i=0;i<=320;i++) {
		sprintf(fn, "/pc/wario/kart%03d.raw.enc", i);
		ssize_t fnsize = fs_load(fn, &all_karts[6][i]);
//		printf("load %s %d\n", fn, fnsize);
	}
	for(int i=0;i<=320;i++) {
		sprintf(fn, "/pc/yoshi/kart%03d.raw.enc", i);
		ssize_t fnsize = fs_load(fn, &all_karts[7][i]);
//		printf("load %s %d\n", fn, fnsize);
	}

	for(int i=0;i<8;i++)
		pvr_kart[i] = pvr_mem_malloc(64*64);

        pvr_set_pal_format(PVR_PAL_ARGB1555);

        // color 0 is always transparent (replacing RGB ff 00 ff)
        pvr_set_pal_entry(0, 0);
        for (int i = 1; i < 256; i++)
                pvr_set_pal_entry(i, get_color_argb1555(palette[i][0], palette[i][1], palette[i][2],1));

}

int filter = 1;

void draw_kart(int i, int j, int x, int y, int w, int h, pvr_poly_hdr_t *hdr, pvr_vertex_t *kv) {
	DecodeJaguar(all_karts[i][j],decodebuf);
	pvr_txr_load(decodebuf, pvr_kart[i], 64*64);

	kv[0].x = x;
	kv[0].y = y+h;
	kv[0].u = 0;
	kv[0].v = 1;

	kv[1].x = x;
	kv[1].y = y;
	kv[1].u = 0;
	kv[1].v = 0;

	kv[2].x = x+w;
	kv[2].y = y+h;
	kv[2].u = 1;
	kv[2].v = 1;

	kv[3].x = x+w;
	kv[3].y = y;
	kv[3].u = 1;
	kv[3].v = 0;

	pvr_prim(hdr,32);
	pvr_prim(kv,128);
}

int main(int argc, char **argv) {
pvr_poly_hdr_t kart_hdr[8];
pvr_poly_cxt_t ccxt;
pvr_vertex_t kv[4];

	pvr_init(&pvr_params);
	kv[0].flags = kv[1].flags = kv[2].flags = PVR_CMD_VERTEX;
	kv[3].flags = PVR_CMD_VERTEX_EOL;
	kv[0].z = kv[1].z = kv[2].z = kv[3].z = 5.0f;
	kv[0].argb = kv[1].argb = kv[2].argb = kv[3].argb = 0xFFFFFFFF;



	load_all_karts();
	pvr_set_bg_color(0.0f,0.0f,1.0f);

	for (int i=0;i<8;i++) {
	pvr_poly_cxt_txr(&ccxt, PVR_LIST_TR_POLY, (PVR_TXRFMT_PAL8BPP | PVR_TXRFMT_8BPP_PAL(0) | PVR_TXRFMT_TWIDDLED), 64, 64, pvr_kart[i], (!!filter)*2);
	ccxt.gen.culling = PVR_CULLING_NONE;
	pvr_poly_compile(&kart_hdr[i], &ccxt);
	}
uint16_t old_buttons = 0, rel_buttons = 0;

	while(1) {
pvr_set_zclip(0.000005f);
	for (int i=0;i<321;i++) {
	maple_device_t *cont;
	cont_state_t *state;

	cont = maple_enum_type(0, MAPLE_FUNC_CONTROLLER);
	if (cont) {
	state = (cont_state_t *)maple_dev_status(cont);
 	rel_buttons = (old_buttons ^ state->buttons);

	if ((state->buttons & CONT_START) && state->ltrig && state->rtrig)
		return 0;
	}
	if ((state->buttons & CONT_A)&& (rel_buttons & CONT_A)) {
		filter = !filter;
	for (int i=0;i<8;i++) {
	pvr_poly_cxt_txr(&ccxt, PVR_LIST_TR_POLY, (PVR_TXRFMT_PAL8BPP | PVR_TXRFMT_8BPP_PAL(0) | PVR_TXRFMT_TWIDDLED), 64, 64, pvr_kart[i], (!!filter)*2);
	ccxt.gen.culling = PVR_CULLING_NONE;
	pvr_poly_compile(&kart_hdr[i], &ccxt);
	}

	}
	old_buttons = state->buttons;

	pvr_scene_begin();
	pvr_list_begin(PVR_LIST_TR_POLY);
//		pvr_prim(&kart_hdr,32);
//		pvr_prim(kv,128);
	draw_kart(0,i,0,0,128,128,&kart_hdr[0],kv);

	draw_kart(1,i,128,0,128,128,&kart_hdr[1],kv);

	draw_kart(2,i,256,0,128,128,
&kart_hdr[2],
kv);

	draw_kart(3,i,384,0,128,128,&kart_hdr[3],
kv);

	draw_kart(4,i,0,128,128,128,&kart_hdr[4],
kv);

	draw_kart(5,i,128,128,128,128,&kart_hdr[5],
kv);

	draw_kart(6,i,256,128,128,128,&kart_hdr[6],
kv);

	draw_kart(7,i,384,128,128,128,&kart_hdr[7],
kv);

	pvr_list_finish();
	pvr_scene_finish();
	}
	}
	return 0;
}
