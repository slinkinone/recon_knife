FROM debian:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV GOLANG_VERSION=1.13.4
ENV TERM=xterm
ENV HOME /root

# Global dependencies
RUN apt-get -y update && \
	apt-get install -y --no-install-recommends \
	less \
	mc \
	file \
	vim-tiny \
	vim \
	dnsutils \
	apt-utils \
	git \
	nmap \
	rename \
	awscli \
	snapd \
	wget \
	curl \
	libcurl4-openssl-dev \
	libssl-dev \
	jq \
	ruby-full \
	ruby-dev \
	libxml2 \
	libxml2-dev \
	libxslt1-dev \
	libgmp-dev \
	zlib1g-dev \
	build-essential \
	libffi-dev \
	libldns-dev \
	python2 \
	python3 \
	python-dev \
	python-setuptools \
	python3-pip \
	python-pip \
	python-dnspython \
	chromium \
	&& rm -rf /var/lib/apt/lists/*


RUN mkdir -p /root/.aws
COPY ./aws_credentials.txt /root/.aws/credentials

# Golang installing
RUN go_url=https://dl.google.com/go/go${GOLANG_VERSION}.linux-amd64.tar.gz && \
	wget -O go.tgz "$go_url" && \
	tar -C /usr/local -xzf go.tgz && \
	rm go.tgz && \
	export PATH="/usr/local/go/bin:$PATH" && \
	go version

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH
RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"

# bbht installing
RUN mkdir $HOME/tools
WORKDIR $HOME/tools/

# TODO: Is really required?
#RUN echo "Installing bash_profile aliases from recon_profile"
#RUN git clone https://github.com/nahamsec/recon_profile.git
#RUN cd recon_profile && cat .bash_profile >> $HOME/.bash_profile
#RUN ["/bin/bash", "-c", "source $HOME/.bash_profile"]

RUN echo "Installing Aquatone"
RUN go get github.com/michenriksen/aquatone

#RUN echo "Installing Chromium"
#RUN systemctl status snapd
#RUN snap install chromium

#RUN echo "Installing JSParser"
#RUN git clone https://github.com/nahamsec/JSParser.git
#RUN cd JSParser* && pip2 install 'soupsieve==1.9.5' && python setup.py install

RUN echo "Installing Sublist3r"
RUN git clone https://github.com/aboul3la/Sublist3r.git
RUN cd Sublist3r* && pip3 install -r requirements.txt

RUN echo "Installing teh_s3_bucketeers"
RUN git clone https://github.com/tomdev/teh_s3_bucketeers.git

RUN echo "Installing wpscan"
RUN git clone https://github.com/wpscanteam/wpscan.git
RUN cd wpscan* && gem install bundler && bundle install --without test

RUN echo "Installing dirsearch"
RUN git clone https://github.com/maurosoria/dirsearch.git

RUN echo "Installing lazys3"
RUN git clone https://github.com/nahamsec/lazys3.git

RUN echo "Installing virtual host discovery"
RUN git clone https://github.com/jobertabma/virtual-host-discovery.git

RUN echo "Installing sqlmap"
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev

RUN echo "Installing knock.py"
RUN git clone https://github.com/guelfoweb/knock.git

RUN echo -"Installing massdns"
RUN git clone https://github.com/blechschmidt/massdns.git
RUN cd massdns && make

RUN echo "Installing asnlookup"
RUN git clone https://github.com/yassineaboukir/asnlookup.git
RUN cd asnlookup && pip install wheel && pip install -r requirements.txt

RUN echo "Installing httprobe"
RUN go get -u github.com/tomnomnom/httprobe 

RUN echo "Installing unfurl"
RUN go get -u github.com/tomnomnom/unfurl 

RUN echo "Installing waybackurls"
RUN go get github.com/tomnomnom/waybackurls

RUN echo "Installing crtndstry"
RUN git clone https://github.com/nahamsec/crtndstry.git

RUN echo "Downloading Seclists"
RUN git clone https://github.com/danielmiessler/SecLists.git
# THIS FILE BREAKS MASSDNS AND NEEDS TO BE CLEANED
RUN cd SecLists/Discovery/DNS/ && cat dns-Jhaddix.txt | head -n -14 > clean-jhaddix-dns.txt

RUN echo "Installing JSParser"
RUN git clone https://github.com/nahamsec/JSParser.git
RUN cd JSParser* && pip2 install 'soupsieve==1.9.5'\
	&& sed -i "s/tornado/tornado==5.1.1/g" setup.py \
	&& python setup.py install

# dependencies for the final script
RUN pip3 install setuptools
RUN pip3 install wheel
RUN pip3 install termcolor

#RUN echo "Installing lazyrecon"
#RUN git clone https://github.com/nahamsec/lazyrecon.git
#RUN cd lazyrecon && sed -i "s/snap\/bin\/chromium/usr\/bin\/chromium/g" lazyrecon.sh

# Running cmd within the container
#ENV HOME=/root
#CMD go version && python2 --version && python3 --version
#CMD cd /data/io_dir
#ENTRYPOINT ["/root/tools/lazyrecon/lazyrecon.sh"]
#CMD $HOME/tools/lazyrecon/* /data/output
