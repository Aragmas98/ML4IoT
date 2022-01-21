from DoSomething import DoSomething

class Subscriber(DoSomething):
    def notify(self, topic, msg):
        print(topic, msg)


if __name__ == '__main__':
    subscriver = Subscriber('subscriber 1')
    subscriver.run() 
    subscriver.myMqttClient.mySubscribe('/ML4IoT/Group17/H3/e1/alert')