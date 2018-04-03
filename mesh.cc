#include <cmath>
#include <cstdio>
#include <iostream>
using namespace std;

const double rr = 25;
const double rout = 745, rin = 395, size = 87.5;
const double z_min = rr, z_max = 200;//10000 + rr;
const double delta_t = M_PI / 6, delta_r = size, delta_z = size*2;
const unsigned nt = 2 * M_PI / delta_t, nr = (rout - rin) / delta_r, nz = z_max/delta_z;
const unsigned fnc = 8, fns = 24;

int main() {
	cout << "nz = " << nz << endl;
	cout << "nr = " << nr << endl;
	cout << "nt = " << nt << endl;
	FILE *fout;
	FILE *fscad;
    fout = fopen("mesh_v.pov","w");
    fscad = fopen("mesh.scad","w");
    fprintf(fscad, "module cylinder_ep(p1,p2,r,fn){\nvector=[p2[0]-p1[0],p2[1]-p1[1],p2[2]-p1[2]];\ndistance=sqrt(pow(vector[0],2)+pow(vector[1],2)+pow(vector[2],2));\ntranslate(vector/2+p1)\nrotate([0,0,atan2(vector[1],vector[0])])\nrotate([0,atan2(sqrt(pow(vector[0], 2)+pow(vector[1], 2)),vector[2]), 0])\ncylinder(h=distance,r1=r,r2=r,center=true,$fn=fn);\n}\nmodule sphere_at(p,r,fn){\ntranslate(p)\nsphere(r,center=true,$fn=fn);\n}\n");
    fprintf(fscad, "fnc=%d; fns=%d; rc=%g; rs=%g;\n", fnc, fns, rr, rr);
    fprintf(fscad, "union() {\n");
	for (unsigned iz = 0; iz < nz; ++iz) {
		for (unsigned ir = 0; ir < nr; ++ir) {
			for (unsigned it = 0; it < nt; ++it) {
				double r1 = rin + delta_r * ir;
				double r2 = r1 + delta_r;
				double z = iz * delta_z;
				bool offset = ir % 2 == 1;
				if (iz % 2 == 1)
					offset = !offset;
				double theta1 = delta_t * it + (offset ? delta_t / 2 : 0);
				double theta2 = theta1 + delta_t / 2;
				double theta3 = theta1 + delta_t;
				double theta4 = theta2;
				double theta5 = theta3;
				double x1 = r1 * cos(theta1), y1 = r1 * sin(theta1), z1 = z;
				double x2 = r2 * cos(theta2), y2 = r2 * sin(theta2), z2 = z;
				double x3 = r1 * cos(theta3), y3 = r1 * sin(theta3), z3 = z;
				double x4 = r1 * cos(theta4), y4 = r1 * sin(theta4), z4 = z + delta_z;
				double x5 = r2 * cos(theta5), y5 = r2 * sin(theta5), z5 = z + delta_z;
				if (ir < nr - 1) {
					fprintf(fout,"cylinder{<%g,%g,%g>,<%g,%g,%g>,r}\n", x1, y1, z1, x2, y2, z2);
					fprintf(fout,"cylinder{<%g,%g,%g>,<%g,%g,%g>,r}\n", x2, y2, z2, x3, y3, z3);
					//
					fprintf(fscad,"cylinder_ep([%g,%g,%g], [%g,%g,%g],rc,fnc);\n", x1, y1, z1, x2, y2, z2);
					fprintf(fscad,"cylinder_ep([%g,%g,%g], [%g,%g,%g],rc,fnc);\n", x2, y2, z2, x3, y3, z3);
				} else {
					fprintf(fout,"sphere{<%g,%g,%g>,r}\n", x1, y1, z1);
					fprintf(fscad,"sphere_at([%g,%g,%g],rs,fns);\n", x1, y1, z1);
				}
				fprintf(fout,"cylinder{<%g,%g,%g>,<%g,%g,%g>,r}\n", x1, y1, z1, x3, y3, z3);
				fprintf(fscad,"cylinder_ep([%g,%g,%g], [%g,%g,%g],rc,fnc);\n", x1, y1, z1, x3, y3, z3);
				if (iz < nz - 1) {
					fprintf(fout,"cylinder{<%g,%g,%g>,<%g,%g,%g>,r}\n", x1, y1, z1, x4, y4, z4);
					fprintf(fout,"cylinder{<%g,%g,%g>,<%g,%g,%g>,r}\n", x3, y3, z3, x4, y4, z4);
					//
					fprintf(fscad,"cylinder_ep([%g,%g,%g], [%g,%g,%g],rc,fnc);\n", x1, y1, z1, x4, y4, z4);
					fprintf(fscad,"cylinder_ep([%g,%g,%g], [%g,%g,%g],rc,fnc);\n", x3, y3, z3, x4, y4, z4);
					if (ir < nr - 1){
						fprintf(fout,"cylinder{<%g,%g,%g>,<%g,%g,%g>,r}\n", x2, y2, z2, x5, y5, z5);
						fprintf(fout,"cylinder{<%g,%g,%g>,<%g,%g,%g>,r}\n", x3, y3, z3, x5, y5, z5);
						//
						fprintf(fscad,"cylinder_ep([%g,%g,%g], [%g,%g,%g],rc,fnc);\n", x2, y2, z2, x5, y5, z5);
						fprintf(fscad,"cylinder_ep([%g,%g,%g], [%g,%g,%g],rc,fnc);\n", x3, y3, z3, x5, y5, z5);
					}
				}
			}
		}
	}
	fprintf(fscad, "}\n");
  	fclose(fout);
  	fclose(fscad);
}
