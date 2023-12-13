сервис обрабатывает статистику с сайта understat.com

добавить тур можно с помощью http://localhost:8080/add_tour, добавленные матчи отобразятся на http://localhost:8080/matches/{турнир}/{номер тура}
чтобы посмотреть все доступные матчи можно вернуться на http://localhost:8080/matches

получить отчет по выбранному матчу http://localhost:8080/report/{match_id} (match_id каждого матча отображается при их выводе)
(например http://localhost:8080/report/22018)

получить отчет по туру http://localhost:8080/report/{турнир}/{номер тура}
(например http://localhost:8080/report/EPL/1)
