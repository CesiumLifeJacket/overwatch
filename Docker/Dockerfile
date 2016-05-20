#*********************************************************************************
#    ___         _     ___ _        _   _     
#   / __|___  __| |___/ __| |_ _  _| | (_)___ 
#  | (__/ _ \/ _` / -_)__ \  _| || | |_| / _ \
#   \___\___/\__,_\___|___/\__|\_, |_(_)_\___/
#                              |__/                                                         
#
#
# Originaly developed by students of Whitworth University -> http://www.whitworth.edu/cms/
# 
# Incepted and maintained by Will Czifro -> will@czifrotech.com
#
#
# This software is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY
# KIND, either express or implied.
#
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

## install apache, php and pear
RUN apt-get install -y apache2
RUN apt-get install -y php5
RUN apt-get install -y libapache2-mod-php5
RUN etc/init.d/apache2 restart

RUN apt-get install -y php-pear
RUN pear install PHP_CodeSniffer

## create directory for host computer's project
RUN mkdir /hostdata

## append line to Image's .bashrc to start bash in hostdata
RUN echo "cd /hostdata" >> ~/.bashrc

## 