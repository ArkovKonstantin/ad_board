FROM python:3.8
ADD . /ad_board
WORKDIR /ad_board
RUN pip install -r requirements.txt
#EXPOSE 8001
#CMD python -m api.main