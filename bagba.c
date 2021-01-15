
#include "run.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]){
	
	FILE *fp = fopen("compileself.bidk", "r");
	fseek(fp, 0L, SEEK_END);
	size_t code_size = ftell(fp);
	rewind(fp);
	uint32_t *code = malloc(sizeof(uint32_t) * code_size + 10);
	fread(code, sizeof(uint32_t), code_size, fp);
	int result = run(code, code_size);
	free(code);
	fclose(fp);
	return result;
}
