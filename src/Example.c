#include "mujoco.h"
#include "stdio.h"

char error[1000];
mjModel* m;
mjData* d;

int main(void){
	mj_activate("mjkey.txt");
	
	m = mj_loadXML("Single_RP_Leg.xml", NULL, error, 1000);
	if (!m){
		printf("%s\n", error);
		return 1
	}
	d = mj_makeData(m);
	
	while(d->time<10)
		mj_step(m, d);
	
	mj_deleteData(d);
	mj_deleteModel(m);
	mj_deactivate();
	
	return 0;
	
}