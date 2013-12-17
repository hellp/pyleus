import logging

from pyleus.storm import SimpleBolt

from micro.rates_generator import ExchangeRate

log = logging.getLogger('conversions')

SHORT = {"pound": "GBP", "euro": "EUR"}


class ConverterBolt(SimpleBolt):

    OUTPUT_FIELDS = {
        "pound": ["value"],
        "euro": ["value"]
    }

    def initialize(self, conf, context, _):
        self.rates = {"pound": 1., "euro": 1.}

    def process_tuple(self, tup):
        if tup.component == "micro-transactions":
            if tup.stream not in self.rates:
                raise ValueError("Unknown stream: {0}".format(tup.stream))
            value, = tup.values
            converted = value * self.rates[tup.stream]
            log.debug("{0} {1} -> USD{2} ({3})".format(
                SHORT[tup.stream], value, converted, self.rates[tup.stream]))
            self.emit((converted,), tup.stream)

        elif tup.component == "exchange-rates":
            rate = ExchangeRate(*tup.values)
            self.rates[rate.currency] = rate.rate

        else:
            raise ValueError("Unknown component: {0}".format(tup.component))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/tmp/conversions.log',
        format="%(message)s",
        filemode='a',
    )

    ConverterBolt().run()
