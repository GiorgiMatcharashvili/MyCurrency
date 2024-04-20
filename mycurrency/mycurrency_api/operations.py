from .models import CurrencyExchangeRate, Currency
from django.conf import settings
from datetime import datetime, timedelta
from .adapters import Adapter
from .serializers import CurrencySerializer, CurrencyExchangeRateSerializer

# Accessing an available currencies from settings
AVAILABLE_CURRENCIES = settings.AVAILABLE_CURRENCIES

ProviderAdapter = Adapter()


def store_exchange_data(
    source_currency: Currency,
    exchanged_currency: Currency,
    date: str,
    rate_value: float,
) -> None:
    """
    Stores exchange rate into the database
    """
    data = {
        "source_currency": source_currency.pk,
        "exchanged_currency": exchanged_currency.pk,
        "valuation_date": date,
        "rate_value": rate_value,
    }

    serializer = CurrencyExchangeRateSerializer(data=data)
    if serializer.is_valid():
        serializer.save()


def get_exchange_data(
    source_currency: Currency, exchanged_currency: Currency, date: str
) -> float:
    """
    Getting exchange rate from database,
    As an extra option getting reversed rate where source_currency is exchanged and exchanged_currency is source,
    using the logic that rate_value for from source to exchanged transaction is
    1/rate_value for exchanged to source transaction. Using this method we can store half as data into the database.
    """
    rate = CurrencyExchangeRate.objects.filter(
        source_currency=source_currency,
        exchanged_currency=exchanged_currency,
        valuation_date=date,
    )

    if rate.exists():
        return float(rate.first().rate_value)

    reversed_rate = CurrencyExchangeRate.objects.filter(
        source_currency=exchanged_currency,
        exchanged_currency=source_currency,
        valuation_date=date,
    )

    if reversed_rate.exists():
        return float(1 / reversed_rate.first().rate_value)


def check_currency(symbol: str) -> Currency:
    """
    In case of founding non-familiar currency which is available, checks with providers if it's possible to gather
    more data about this currency.
    """
    currency_inst = Currency.objects.filter(code=symbol).first()

    if not currency_inst:
        symbols = ProviderAdapter.get_currency_symbols()["symbols"]

        # This currency is supported
        data = {"code": symbol, "name": symbols[symbol], "symbol": symbol}
        serializer = CurrencySerializer(data=data)
        if serializer.is_valid():
            currency_inst = serializer.save()

    return currency_inst


def get_currency_rates(
    source_currency: list, date_from: list, date_to: list, *args, **kwargs
) -> dict:
    """
    Gathering a currency rates from date_from to date_to for every available currencies.
    """

    # Upack variables
    source_currency = source_currency[0]
    date_from = date_from[0]
    date_to = date_to[0]

    # Check if currency is supported
    if source_currency not in AVAILABLE_CURRENCIES:
        raise ValueError(f"{source_currency} is not in available currencies.")

    target_currencies = [x for x in AVAILABLE_CURRENCIES if x != source_currency]

    source_currency = check_currency(source_currency)

    # Turn string dates into datetime
    start = datetime(*[int(i) for i in date_from.split("-")]).date() - timedelta(days=1)
    end = datetime(*[int(i) for i in date_to.split("-")]).date()

    final_rates = {}

    while start != end:
        # for every date from start date to end date
        start = start + timedelta(days=1)
        date = str(start)
        for exchanged_currency in target_currencies:
            exchanged_currency = check_currency(exchanged_currency)
            if exchanged_currency:
                # Check in Database
                rate_value = get_exchange_data(
                    source_currency, exchanged_currency, date
                )

                if not rate_value:
                    # Ask provider if it exists in the Database
                    provider_data = ProviderAdapter.get_exchange_rate_data(
                        source_currency.code,
                        exchanged_currency.code,
                        date,
                        *args,
                        **kwargs,
                    )

                    rate_value = round(
                        provider_data["rates"][exchanged_currency.code], 6
                    )

                    store_exchange_data(
                        source_currency, exchanged_currency, date, rate_value
                    )

                if not final_rates.get(date, False):
                    final_rates[date] = {exchanged_currency.code: rate_value}
                else:
                    final_rates[date].update({exchanged_currency.code: rate_value})

    return {
        "source_currency": str(source_currency.code),
        "date_from": str(date_from),
        "date_to": str(date_to),
        "rates": final_rates,
    }


def get_converted_data(
    source_currency: list, amount: list, exchanged_currency: list, *args, **kwargs
) -> dict:
    """
    Converts amount of money from source currency to exchanged currency.
    """
    # Upack variables
    source_currency = source_currency[0]
    exchanged_currency = exchanged_currency[0]
    amount = float(amount[0])

    # Check if currencies are supported
    if source_currency not in AVAILABLE_CURRENCIES:
        raise ValueError(f"{source_currency} is not in available currencies.")

    if exchanged_currency not in AVAILABLE_CURRENCIES:
        raise ValueError(f"{exchanged_currency} is not in available currencies.")

    source_currency = check_currency(source_currency)
    exchanged_currency = check_currency(exchanged_currency)

    # Get today's date
    date = datetime.now().date()

    rate_value = get_exchange_data(source_currency, exchanged_currency, date)

    if not rate_value:
        # Ask provider to convert currencies if rate value is not in database
        converted_data = ProviderAdapter.convert_currencies(
            source_currency.code, exchanged_currency.code, amount, *args, **kwargs
        )

        rate_value = round(converted_data["info"]["rate"], 6)

        store_exchange_data(source_currency, exchanged_currency, date, rate_value)

        converted_amount = converted_data["result"]

    else:
        converted_amount = amount * rate_value

    return {
        "source_currency": str(source_currency.code),
        "exchanged_currency": str(exchanged_currency.code),
        "initial_amount": str(amount),
        "rate": str(rate_value),
        "result": str(converted_amount),
    }


def get_twrr_values(
    source_currency: list,
    amount: list,
    exchanged_currency: list,
    start_date: list,
    *args,
    **kwargs,
) -> dict:
    """
    Calculates TWRR for the amount transacted from source_currency to exchanged_currency at start_date to today.
    """
    # Upack variables
    source_currency = source_currency[0]
    amount = float(amount[0])
    exchanged_currency = exchanged_currency[0]
    start_date = start_date[0]

    # Check if currencies are supported
    if source_currency not in AVAILABLE_CURRENCIES:
        raise ValueError(f"{source_currency} is not in available currencies.")

    if exchanged_currency not in AVAILABLE_CURRENCIES:
        raise ValueError(f"{exchanged_currency} is not in available currencies.")

    source_currency = check_currency(source_currency)
    exchanged_currency = check_currency(exchanged_currency)

    # Get today's date
    date = datetime.now().date()

    start = datetime(*[int(i) for i in start_date.split("-")]).date() - timedelta(
        days=1
    )

    initial_value = 0

    twr_plus_one = 1

    twrr_values = dict()

    while start != date:
        start = start + timedelta(days=1)
        rate_value = get_exchange_data(source_currency, exchanged_currency, str(start))

        if not rate_value:
            provider_data = ProviderAdapter.get_exchange_rate_data(
                source_currency.code,
                exchanged_currency.code,
                str(start),
                *args,
                **kwargs,
            )

            rate_value = round(provider_data["rates"][exchanged_currency.code], 6)

            store_exchange_data(
                source_currency, exchanged_currency, str(start), rate_value
            )

        if str(start) == start_date:
            initial_value = round(amount * rate_value, 6)

        # Formula for calculating TWRR
        exchanged_value = round(amount * rate_value, 6)

        sub_period = round((exchanged_value - initial_value) / initial_value, 6)

        twr = round((twr_plus_one * (1 + sub_period)) - 1, 6)

        twrr_values[str(start)] = twr

    return {
        "source_currency": str(source_currency.code),
        "exchanged_currency": str(exchanged_currency.code),
        "initial_amount": str(amount),
        "start_date": str(start_date),
        "result": twrr_values,
    }
