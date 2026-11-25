USE library;

SELECT b.book_id, b.title, b.price, b.publish_year, a.name AS author, c.name AS category
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
JOIN CATEGORY c ON b.category_id = c.category_id
WHERE b.title LIKE '%Harry%'
  AND b.price BETWEEN 10 AND 30
  AND b.category_id = 1
ORDER BY b.price ASC;

SELECT b.book_id, b.title, b.price, b.publish_year,
       a.name AS author_name, p.name AS publisher_name, c.name AS category_name
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
JOIN CATEGORY c ON b.category_id = c.category_id
ORDER BY b.book_id ASC;

SELECT c.name AS category_name, COUNT(b.book_id) AS total_books, ROUND(AVG(b.price), 2) AS avg_price
FROM CATEGORY c
LEFT JOIN BOOK b ON c.category_id = b.category_id
GROUP BY c.category_id, c.name;

SELECT a.name AS author_name, COUNT(b.book_id) AS book_count
FROM AUTHOR a
JOIN BOOK b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(b.book_id) >= 2;

SELECT SUM(price) AS total_price, MIN(price) AS min_price, MAX(price) AS max_price
FROM BOOK;

SELECT l.loan_id, b.title AS book_title, m.name AS member_name, l.loan_date
FROM LOAN l
JOIN BOOK b ON l.book_id = b.book_id
JOIN MEMBER m ON l.member_id = m.member_id
WHERE l.return_date IS NULL;

SELECT m.member_id, m.name, m.email, m.join_date
FROM MEMBER m
LEFT JOIN LOAN l ON m.member_id = l.member_id
WHERE l.loan_id IS NULL;

SELECT b.book_id, b.title, b.price, b.publish_year
FROM BOOK b
LEFT JOIN LOAN l ON b.book_id = l.book_id
WHERE l.loan_id IS NULL;

SELECT b.title, COUNT(l.loan_id) AS loan_count
FROM BOOK b
JOIN LOAN l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title
ORDER BY loan_count DESC
LIMIT 3;

SELECT m.name, COUNT(l.loan_id) AS loan_count
FROM MEMBER m
JOIN LOAN l ON m.member_id = l.member_id
GROUP BY m.member_id, m.name
ORDER BY loan_count DESC
LIMIT 1;

SELECT a.name AS author_name, a.country, COUNT(b.book_id) AS books_written
FROM AUTHOR a
LEFT JOIN BOOK b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name, a.country;

SELECT b.title, a.name AS author_name, p.name AS publisher_name, a.country
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country;

SELECT title, price,
       ROUND((SELECT AVG(price) FROM BOOK), 2) AS avg_library_price
FROM book_details
WHERE price > (SELECT AVG(price) FROM BOOK)
ORDER BY price DESC;

SELECT b.book_id, b.title, b.price, b.publish_year
FROM BOOK b
WHERE NOT EXISTS (
    SELECT * FROM LOAN l WHERE l.book_id = b.book_id
);

SELECT m.member_id, m.name, m.email, m.join_date
FROM MEMBER m
WHERE NOT EXISTS (
    SELECT * FROM LOAN l WHERE l.member_id = m.member_id
);

SELECT bd.category_name, bd.title, bd.price
FROM book_details bd
WHERE bd.price = (
    SELECT MAX(b2.price)
    FROM BOOK b2
    WHERE b2.category_id = bd.category_id
);

SELECT bd.category_name, bd.title, bd.price
FROM book_details bd
WHERE bd.price > (
    SELECT AVG(b2.price)
    FROM BOOK b2
    WHERE b2.category_id = bd.category_id
);

SELECT m.member_id, m.name, COUNT(l.loan_id) AS loan_count,
       ROUND(avg_table.avg_loans, 2) AS avg_loans_per_member
FROM MEMBER m
LEFT JOIN LOAN l ON m.member_id = l.member_id
CROSS JOIN (
    SELECT AVG(cnt) AS avg_loans
    FROM (
        SELECT COUNT(l2.loan_id) AS cnt
        FROM MEMBER m2
        LEFT JOIN LOAN l2 ON m2.member_id = l2.member_id
        GROUP BY m2.member_id
    ) member_counts
) avg_table
GROUP BY m.member_id, m.name, avg_table.avg_loans
HAVING COUNT(l.loan_id) > avg_table.avg_loans;

SELECT a.author_id, a.name, a.country
FROM AUTHOR a
WHERE EXISTS (
    SELECT *
    FROM BOOK b
    JOIN LOAN l ON b.book_id = l.book_id
    WHERE b.author_id = a.author_id
);

SELECT b.book_id, b.title,
       COUNT(r.review_id) AS review_count,
       ROUND(COALESCE(AVG(r.rating), 0), 2) AS avg_rating,
       CASE
           WHEN COUNT(r.review_id) = 0 THEN 'No review'
           WHEN AVG(r.rating) >= 4.5 THEN 'Excellent'
           WHEN AVG(r.rating) >= 3.5 THEN 'Good'
           ELSE 'Fair'
       END AS rating_label
FROM BOOK b
LEFT JOIN REVIEW r ON b.book_id = r.book_id
GROUP BY b.book_id, b.title;

SELECT b.book_id, b.title,
       ROUND(AVG(r.rating), 2) AS avg_rating
FROM BOOK b
JOIN REVIEW r ON b.book_id = r.book_id
GROUP BY b.book_id, b.title
HAVING AVG(r.rating) > (SELECT AVG(rating) FROM REVIEW);

SELECT country FROM AUTHOR
UNION
SELECT country FROM PUBLISHER
ORDER BY country;

SELECT country FROM AUTHOR
INTERSECT
SELECT country FROM PUBLISHER;

SELECT country FROM AUTHOR
EXCEPT
SELECT country FROM PUBLISHER;

SELECT name, 'Author' AS type FROM AUTHOR
UNION ALL
SELECT name, 'Member' AS type FROM MEMBER
ORDER BY name;