import requests
from bs4 import BeautifulSoup


def get_schedule(selected_date=None):
    # Fetch the HTML page
    response = requests.get("https://multiplex.ua/cinema/lviv/spartak")
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    # Find the container that holds the schedule data
    container = soup.find("div", class_="cinema_schedule_films")
    if not container:
        raise Exception("Could not find the schedule container in the HTML.")

    schedule = {}

    # The schedule is divided by date, in div elements with class "cinema_inside"
    for date_block in container.find_all("div", class_="cinema_inside"):
        date = date_block["data-date"]
        schedule[date] = []  # initialize list for movies on this date

        # Each movie is contained in a div with the class "film"
        for film in date_block.find_all("div", class_="film"):
            movie = {}

            # Extract movie title from the <a> tag with a title attribute,
            # or fallback to the link inside the "info" block.
            poster_link = film.find("a", title=True)
            if poster_link:
                movie["title"] = poster_link["title"]
            else:
                info_title = film.find("a", class_="title")
                movie["title"] = info_title.get_text(strip=True) if info_title else "Unknown Title"

            # Extract the age filter if present, else set as "N/A"
            age_elem = film.find("span", class_="age")
            movie["age"] = age_elem.get_text(strip=True) if age_elem else "N/A"

            # Find the block that contains session information
            info = film.find("div", class_="info")
            sessions = []
            if info:
                sessions_div = info.find("div", class_="sessions")
                if sessions_div:
                    # Each session is an <a> element (with class "ns")
                    for session in sessions_div.find_all("a", class_="ns"):
                        # Extract the session time (contained in a <p class="time"> tag)
                        time_elem = session.find("p", class_="time")
                        time_str = time_elem.get_text(strip=True) if time_elem else None

                        # Extract lowest and highest price from the attributes
                        low_price = session.get("data-low")
                        high_price = session.get("data-high")

                        sessions.append({
                            "time": time_str,
                            "lowest_price": low_price,
                            "highest_price": high_price,
                        })
            movie["sessions"] = sessions
            schedule[date].append(movie)
    if selected_date:
        return schedule.get(selected_date, [])
    return schedule
