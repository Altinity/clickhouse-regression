-- Q7. Percentage of flights delayed for more than 10 minutes, by year
SELECT Year, avg(DepDelay>10)*100
FROM ontime
GROUP BY Year
ORDER BY Year;
