FROM ghcr.io/gem5/ubuntu-22.04_all-dependencies:v23-0

# Work in root
WORKDIR /

# Clone gem5 source
RUN git clone https://gem5.googlesource.com/public/gem5

# Enter gem5 directory
WORKDIR /gem5

# Build ARM gem5 once (this is the 1-hour step)
RUN scons build/ARM/gem5.opt -j$(nproc)

# Default shell
CMD ["/bin/bash"]
