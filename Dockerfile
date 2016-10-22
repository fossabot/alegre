# alegre

FROM meedan/ruby
MAINTAINER sysops@meedan.com

#
# SYSTEM CONFIG
#
ENV DEPLOYUSER=mlgdeploy \
    DEPLOYDIR=/var/www/alegre \
    RAILS_ENV=production \
    GITREPO=git@github.com:meedan/alegre.git

RUN apt-get install gcc python python-setuptools libpython-dev python2.7-dev vim gfortran libatlas-base-dev nodejs libmysqlclient-dev -y
RUN easy_install pip

#
# APP CONFIG
#

# nginx for alegre
COPY docker/nginx.conf /etc/nginx/sites-available/alegre
RUN ln -s /etc/nginx/sites-available/alegre /etc/nginx/sites-enabled/alegre \
    && rm /etc/nginx/sites-enabled/default

#
# USER CONFIG
#

RUN useradd ${DEPLOYUSER} -s /bin/bash -m \
    && chown -R ${DEPLOYUSER}:${DEPLOYUSER} /home/${DEPLOYUSER}

#
# code deployment
#

RUN mkdir -p $DEPLOYDIR \
    && chown www-data:www-data /var/www \
    && chmod 775 /var/www \
    && chmod g+s /var/www

WORKDIR ${DEPLOYDIR}
RUN mkdir ./latest
COPY ./Gemfile ./latest/Gemfile
COPY ./Gemfile.lock ./latest/Gemfile.lock

# Install and link libraries to the place that RubyPython looks for them
COPY ./requirements.txt ./latest/requirements.txt
COPY docker/link-python-libs /usr/local/bin/link-python-libs
RUN pip install -r ./latest/requirements.txt 
RUN chmod +x /usr/local/bin/link-python-libs && sleep 1 \    
    && /usr/local/bin/link-python-libs

RUN chown -R ${DEPLOYUSER}:www-data ${DEPLOYDIR}
USER ${DEPLOYUSER}

RUN echo "gem: --no-rdoc --no-ri" > ~/.gemrc \
    && cd ./latest \
    && bundle install --deployment --without test development

USER root
COPY . ./latest
RUN chown -R ${DEPLOYUSER}:www-data ${DEPLOYDIR}
USER ${DEPLOYUSER}

# config
RUN cd ./latest/config \
    && rm -f ./database.yml && ln -s ${DEPLOYDIR}/shared/config/database.yml ./database.yml \
    && rm -f ./config.yml && ln -s ${DEPLOYDIR}/shared/config/config.yml ./config.yml \
    && cd ./initializers \
    && rm -f ./errbit.rb && ln -s ${DEPLOYDIR}/shared/config/initializers/errbit.rb ./errbit.rb \
    && rm -f ./secret_token.rb && ln -s ${DEPLOYDIR}/shared/config/initializers/secret_token.rb ./secret_token.rb

RUN mv ./latest ./alegre-$(date -I) && ln -s ./alegre-$(date -I) ./current

#
# RUNTIME ELEMENTS
# expose, cmd

USER root
WORKDIR ${DEPLOYDIR}/current
EXPOSE 80
CMD ["nginx"]
