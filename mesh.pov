#version 3.6;

// Right-handed coordinate system in which the z axis points upwards
camera {
	location <2000,-5000,5000>
	sky z
	right -0.4*x*image_width/image_height
	up 0.4*z
	look_at <0,0,0>
}

// White background
background{rgb 1}

// Two lights with slightly different colors
light_source{<-800,-2000,3000> color rgb <0.77,0.75,0.75>}
light_source{<2000,-1500,50> color rgb <0.38,0.40,0.40>}
light_source{<0,0,0> color rgb <0.77,0.75,0.75>}

// Radius of the Voronoi cell network, and the particle radius
#declare r=25;

// Voronoi cells
#declare My_Object = 
union{
#include "mesh_v.pov"
scale <1,-1,1>	
pigment{rgb <0.5,0.8,1>} finish{specular 0.5 ambient 0.42}
}
object {My_Object}
// #include "pov2mesh.pov"
// All_Trace(My_Object,<-770,-770,-25>,<770,770,300>,5,5,5)