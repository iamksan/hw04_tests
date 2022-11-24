from datetime import date


def year(request):
    today = date.today()
    return {'year': today.year}
