FROM ai-env

USER root

ENV PYTHONPATH=/camera-service
ENV TZ=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /camera-service

COPY ./ /camera-service

EXPOSE 8002

CMD ["python3", "/camera-service/src/app.py"]