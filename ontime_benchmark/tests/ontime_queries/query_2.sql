-- Q2. The number of flights delayed by more than 10 minutes, grouped by the day of the week, for 2000-2008
SELECT DayOfWeek, count(*) AS c
FROM ontime
WHERE DepDelay>10 AND Year>=2000 AND Year<=2008
GROUP BY DayOfWeek
ORDER BY c DESC;
