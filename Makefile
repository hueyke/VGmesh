EXECUTABLES=mesh
include $(mesh.deps)

all: $(EXECUTABLES)

mesh: mesh.cc
	$(CXX) -O3 -o mesh mesh.cc

pov: mesh.pov
	povray +W600 +H600 +A0.3 +Omesh.png +GDmesh.asc mesh.pov

stl: mesh.scad
	openscad -m make -o mesh.stl -D 'quality="production"' mesh.scad

clean:
	rm -f $(EXECUTABLES)
	rm -f *.png

.PHONY: all clean
