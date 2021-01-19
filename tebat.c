
#include "run.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]){
	
	if (argc != 2){
		fprintf(stderr, "%s takes one filename as argument", argv[0]);
		return -1;
	}
	FILE *fp = fopen(argv[1], "rb");
	fseek(fp, 0L, SEEK_END);
	size_t code_size = ftell(fp);
	rewind(fp);
	uint32_t *code = malloc(sizeof(uint32_t) * code_size + 10);
	fread(code, sizeof(uint32_t), code_size, fp);
	fclose(fp);
	int result = run(code, code_size);
	free(code);
	return result;
}
