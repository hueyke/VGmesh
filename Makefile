EXECUTABLES=mesh

# Makefile rules
all: $(EXECUTABLES)

mesh: mesh.cc
	$(CXX) -O3 -o mesh mesh.cc

pov: mesh.pov
	povray +W600 +H600 +A0.3 +Omesh.png +GDmesh.asc mesh.pov

clean:
	rm -f $(EXECUTABLES)
	rm -f *.png

.PHONY: all clean
