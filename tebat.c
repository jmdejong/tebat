
#include "run.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

uint32_t *hexread(char *fname, size_t *size){
	
	FILE *fp = fopen(fname, "r");
	fseek(fp, 0L, SEEK_END);
	size_t codetext_size = ftell(fp);
	rewind(fp);
	char *codetext = malloc(sizeof(char) * codetext_size);
	fread(codetext, sizeof(char), codetext_size, fp);
	fclose(fp);
	
	size_t nchars = 0;
	for (size_t i=0; i<codetext_size; ++i){
		char c = codetext[i];
		if ((c >= '0' && c <= '9') || (c >= 'A' && c <= 'F') || (c >= 'a' && c <= 'f')){
			++nchars;
		}
	}
	if (nchars % 8){
		printf("Error: number of hex chars must be a multiple of 8\n");
		exit(-1);
	}
	size_t code_size = nchars / 8;
	uint32_t *code = calloc(code_size, sizeof(uint32_t));
	for (size_t i=0, j=0; i<codetext_size; ++i){
		char c = codetext[i];
		uint32_t n;
		if (c >= '0' && c <= '9'){
			n = c - '0';
		} else if (c >= 'A' && c <= 'F'){
			n = c - 'A' + 10;
		} else if (c >= 'a' && c <= 'f'){
			n = c - 'a' + 10;
		} else {
			continue;
		}
		code[j/8] *= 16;
		code[j/8] |= n;
		
		++j;
	}
	free(codetext);
	*size = code_size;
	return code;
}


	
uint32_t *binread(char *fname, size_t *size){
	// todo: enforce endianness
	FILE *fp = fopen(fname, "rb");
	fseek(fp, 0L, SEEK_END);
	size_t code_size = ftell(fp) / sizeof(uint32_t);
	rewind(fp);
	uint32_t *code = malloc(sizeof(uint32_t) * code_size + 10);
	fread(code, sizeof(uint32_t), code_size, fp);
	fclose(fp);
	*size = code_size;
	return code;
}


int main(int argc, char *argv[]){

	if (argc < 2){
		fprintf(stderr, "%s takes at least one argument\n", argv[0]);
		return -1;
	}
	uint32_t *code;
	size_t code_size;
	if (argv[1][0] == '-'){
		if (argc < 3){
			fprintf(stderr, "not enough arguments to %s\n", argv[0]);
			return -1;
		}
		if (!strcmp(argv[1], "--hex")){
			code = hexread(argv[2], &code_size);
		} else {
			fprintf(stderr, "unknown argument %s\n", argv[1]);
			return -1;
		}
	} else {
		code = binread(argv[1], &code_size);
	}
	
	int result = run(code, code_size);
	free(code);
	return result;
}
