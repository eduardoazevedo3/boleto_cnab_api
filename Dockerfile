FROM ruby:2.6

WORKDIR /boleto_api
COPY . .
RUN mkdir -p tmp log
RUN rm start.sh

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y build-essential ghostscript
RUN rm -rf /var/lib/apt/lists/*

RUN gem install bundler
RUN bundle install

CMD bundle exec puma config.ru -w 5
