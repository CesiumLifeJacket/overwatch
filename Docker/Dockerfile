#*********************************************************************************
#
# Patrick Price
# 
#
#
#




## get starting image
FROM ubuntu:14.04
RUN apt-get update

## install git
RUN apt-get install -y git-all

## install stylewatcher python3 dependencies
RUN apt-get install -y python3-pip
RUN pip3 install pyyaml
RUN pip3 install jinja2

## download stylewatcher
RUN git clone https://github.com/CesiumLifeJacket/overwatch.git

## install pep8
RUN pip3 install pep8

## install rubocop
RUN apt-get install -y ruby-full build-essential
RUN gem install rubocop

## create directory for host computer's project
RUN mkdir /hostdata

## append line to Image's .bashrc to start bash in hostdata
RUN echo "cd /hostdata" >> ~/.bashrc

## 