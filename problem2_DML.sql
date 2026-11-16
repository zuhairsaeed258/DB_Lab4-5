USE library;

INSERT INTO AUTHOR (author_id, name, country) VALUES
(1, 'George Orwell', 'UK'),
(2, 'J.K. Rowling', 'UK'),
(3, 'Naguib Mahfouz', 'Egypt'),
(4, 'Robert C. Martin', 'USA'),
(5, 'Haruki Murakami', 'Japan');

INSERT INTO PUBLISHER (publisher_id, name, country) VALUES
(1, 'Penguin Books', 'UK'),
(2, 'Dar Al-Shorouk', 'Egypt'),
(3, 'Prentice Hall', 'USA');

INSERT INTO CATEGORY (category_id, name) VALUES
(1, 'Fiction'),
(2, 'Technology'),
(3, 'History');

INSERT INTO BOOK (book_id, title, price, publish_year, author_id, publisher_id, category_id) VALUES
(1, '1984', 12.00, 1949, 1, 1, 1),
(2, 'Animal Farm', 18.50, 1945, 1, 1, 1),
(3, 'Homage to Catalonia', 22.00, 1938, 1, 1, 3),
(4, 'Harry Potter 1', 25.00, 1997, 2, 1, 1),
(5, 'Harry Potter 2', 27.00, 1998, 2, 1, 1),
(6, 'Palace Walk', 14.00, 1956, 3, 2, 1),
(7, 'Children of Gebelawi', 16.00, 1959, 3, 2, 1),
(8, 'Clean Code', 45.00, 2008, 4, 3, 2),
(9, 'Clean Architecture', 42.00, 2017, 4, 3, 2),
(10, 'The Pragmatic Programmer', 39.00, 1999, 4, 1, 2);

INSERT INTO MEMBER (member_id, name, email, join_date) VALUES
(1, 'Ahmed Ali', 'ahmed@example.com', '2026-01-10'),
(2, 'Sara Hassan', 'sara@example.com', '2026-02-15'),
(3, 'Omar Khaled', 'omar@example.com', '2026-03-01'),
(4, 'Mona Tarek', 'mona@example.com', '2026-04-20'),
(5, 'Youssef Adel', 'youssef@example.com', '2026-05-05');

INSERT INTO LOAN (loan_id, book_id, member_id, loan_date, return_date) VALUES
(1, 1, 1, '2026-06-01', '2026-06-10'),
(2, 1, 2, '2026-06-12', '2026-06-20'),
(3, 1, 3, '2026-07-01', '2026-07-10'),
(4, 4, 1, '2026-07-05', '2026-07-15'),
(5, 4, 4, '2026-07-18', '2026-07-28'),
(6, 8, 1, '2026-08-01', '2026-08-12'),
(7, 8, 2, '2026-08-15', '2026-08-25'),
(8, 2, 3, '2026-09-01', '2026-09-10'),
(9, 6, 1, '2026-09-12', '2026-09-22'),
(10, 7, 2, '2026-10-01', '2026-10-11'),
(11, 3, 1, '2026-11-01', NULL),
(12, 9, 4, '2026-11-05', NULL);