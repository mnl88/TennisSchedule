import logging
import time

from utils.database import engine, session
from utils.models import UserOrm, BookingOrm
from utils.schemas import User, Booking


logger = logging.getLogger(__name__)


def get_bookings(days_depth: int = 7) -> list[Booking]:
    booking_list = []
    future_bookings = session.scalars(BookingOrm.get_future_bookings(days_depth))
    for booking_orm in future_bookings:
        booking = Booking.model_validate(booking_orm)
        user_orm = session.get(UserOrm, booking_orm.user_id)
        booking.user = User.model_validate(user_orm)
        booking_list.append(booking)
    session.close()
    engine.dispose()
    logger.info(f'Получено записей из БД: {len(booking_list)}шт')
    return booking_list


if __name__ == '__main__':
    start_time = time.time()

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    bookings = get_bookings()

    logger.info(f"Execution time: {time.time() - start_time:.2f} seconds")
