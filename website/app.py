from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ZS123456*',
    'database': 'library',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

@app.route('/')
@app.route('/catalogue')
def catalogue():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT b.book_id, b.title, b.price, b.publish_year,
                   a.name AS author_name, p.name AS publisher_name, c.name AS category_name
            FROM BOOK b
            JOIN AUTHOR a ON b.author_id = a.author_id
            JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
            JOIN CATEGORY c ON b.category_id = c.category_id
            ORDER BY b.book_id ASC
        """)
        books = cursor.fetchall()
    conn.close()
    return render_template('catalogue.html', books=books)

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    category_id = request.args.get('category_id', '').strip()

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT category_id, name FROM CATEGORY")
        categories = cursor.fetchall()

        query = """
            SELECT b.book_id, b.title, b.price, b.publish_year,
                   a.name AS author_name, c.name AS category_name
            FROM BOOK b
            JOIN AUTHOR a ON b.author_id = a.author_id
            JOIN CATEGORY c ON b.category_id = c.category_id
            WHERE b.title LIKE %s
              AND b.price BETWEEN %s AND %s
        """
        params = [
            f"%{keyword}%",
            float(min_price) if min_price else 0.0,
            float(max_price) if max_price else 999999.0
        ]

        if category_id:
            query += " AND b.category_id = %s"
            params.append(int(category_id))

        query += " ORDER BY b.price ASC"
        cursor.execute(query, params)
        results = cursor.fetchall()
    conn.close()

    return render_template('search.html', books=results, categories=categories,
                           keyword=keyword, min_price=min_price, max_price=max_price, selected_cat=category_id)

@app.route('/reports')
def reports():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT c.name AS category_name, COUNT(b.book_id) AS total_books, ROUND(AVG(b.price), 2) AS avg_price
            FROM CATEGORY c LEFT JOIN BOOK b ON c.category_id = b.category_id
            GROUP BY c.category_id, c.name
        """)
        cat_stats = cursor.fetchall()

        cursor.execute("""
            SELECT a.name AS author_name, COUNT(b.book_id) AS book_count
            FROM AUTHOR a JOIN BOOK b ON a.author_id = b.author_id
            GROUP BY a.author_id, a.name HAVING COUNT(b.book_id) >= 2
        """)
        prolific_authors = cursor.fetchall()

        cursor.execute("SELECT SUM(price) AS total_price, MIN(price) AS min_price, MAX(price) AS max_price FROM BOOK")
        summary = cursor.fetchone()
    conn.close()
    return render_template('reports.html', cat_stats=cat_stats, prolific_authors=prolific_authors, summary=summary)

@app.route('/loans')
def loans():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT l.loan_id, b.title AS book_title, m.name AS member_name, l.loan_date
            FROM LOAN l JOIN BOOK b ON l.book_id = b.book_id JOIN MEMBER m ON l.member_id = m.member_id
            WHERE l.return_date IS NULL
        """)
        active_loans = cursor.fetchall()

        cursor.execute("""
            SELECT m.member_id, m.name, m.email, m.join_date
            FROM MEMBER m LEFT JOIN LOAN l ON m.member_id = l.member_id
            WHERE l.loan_id IS NULL
        """)
        inactive_members = cursor.fetchall()

        cursor.execute("""
            SELECT b.book_id, b.title, b.price, b.publish_year
            FROM BOOK b LEFT JOIN LOAN l ON b.book_id = l.book_id
            WHERE l.loan_id IS NULL
        """)
        unborrowed_books = cursor.fetchall()
    conn.close()
    return render_template('loans.html', active_loans=active_loans,
                           inactive_members=inactive_members, unborrowed_books=unborrowed_books)

@app.route('/most-borrowed')
def most_borrowed():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT b.title, COUNT(l.loan_id) AS loan_count
            FROM BOOK b JOIN LOAN l ON b.book_id = l.book_id
            GROUP BY b.book_id, b.title ORDER BY loan_count DESC LIMIT 3
        """)
        top_books = cursor.fetchall()

        cursor.execute("""
            SELECT m.name, COUNT(l.loan_id) AS loan_count
            FROM MEMBER m JOIN LOAN l ON m.member_id = l.member_id
            GROUP BY m.member_id, m.name ORDER BY loan_count DESC LIMIT 1
        """)
        top_member = cursor.fetchone()
    conn.close()
    return render_template('most_borrowed.html', top_books=top_books, top_member=top_member)

@app.route('/authors-books')
def authors_books():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT a.name AS author_name, a.country, COUNT(b.book_id) AS books_written
            FROM AUTHOR a LEFT JOIN BOOK b ON a.author_id = b.author_id
            GROUP BY a.author_id, a.name, a.country
        """)
        author_counts = cursor.fetchall()

        cursor.execute("""
            SELECT b.title, a.name AS author_name, p.name AS publisher_name, a.country
            FROM BOOK b JOIN AUTHOR a ON b.author_id = a.author_id JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
            WHERE a.country = p.country
        """)
        local_books = cursor.fetchall()
    conn.close()
    return render_template('authors_books.html', author_counts=author_counts, local_books=local_books)

@app.route('/above-average')
def above_average():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT title, price,
                   ROUND((SELECT AVG(price) FROM BOOK), 2) AS avg_library_price
            FROM book_details
            WHERE price > (SELECT AVG(price) FROM BOOK)
            ORDER BY price DESC
        """)
        books = cursor.fetchall()
    conn.close()
    return render_template('above_average.html', books=books)

@app.route('/never-borrowed')
def never_borrowed():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT b.book_id, b.title, b.price, b.publish_year
            FROM BOOK b
            WHERE NOT EXISTS (
                SELECT * FROM LOAN l WHERE l.book_id = b.book_id
            )
        """)
        unborrowed_books = cursor.fetchall()

        cursor.execute("""
            SELECT m.member_id, m.name, m.email, m.join_date
            FROM MEMBER m
            WHERE NOT EXISTS (
                SELECT * FROM LOAN l WHERE l.member_id = m.member_id
            )
        """)
        inactive_members = cursor.fetchall()
    conn.close()
    return render_template('never_borrowed.html',
                           unborrowed_books=unborrowed_books,
                           inactive_members=inactive_members)

@app.route('/best-category')
def best_category():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT bd.category_name, bd.title, bd.price
            FROM book_details bd
            WHERE bd.price = (
                SELECT MAX(b2.price)
                FROM BOOK b2
                WHERE b2.category_id = bd.category_id
            )
        """)
        most_expensive = cursor.fetchall()

        cursor.execute("""
            SELECT bd.category_name, bd.title, bd.price
            FROM book_details bd
            WHERE bd.price > (
                SELECT AVG(b2.price)
                FROM BOOK b2
                WHERE b2.category_id = bd.category_id
            )
        """)
        above_cat_avg = cursor.fetchall()
    conn.close()
    return render_template('best_category.html',
                           most_expensive=most_expensive,
                           above_cat_avg=above_cat_avg)

@app.route('/active-members')
def active_members():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
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
            HAVING COUNT(l.loan_id) > avg_table.avg_loans
        """)
        active_list = cursor.fetchall()

        cursor.execute("""
            SELECT a.author_id, a.name, a.country
            FROM AUTHOR a
            WHERE EXISTS (
                SELECT *
                FROM BOOK b
                JOIN LOAN l ON b.book_id = l.book_id
                WHERE b.author_id = a.author_id
            )
        """)
        borrowed_authors = cursor.fetchall()
    conn.close()
    return render_template('active_members.html',
                           active_list=active_list,
                           borrowed_authors=borrowed_authors)

@app.route('/reviews')
def reviews():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
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
            GROUP BY b.book_id, b.title
        """)
        all_reviews = cursor.fetchall()

        cursor.execute("""
            SELECT b.book_id, b.title,
                   ROUND(AVG(r.rating), 2) AS avg_rating
            FROM BOOK b
            JOIN REVIEW r ON b.book_id = r.book_id
            GROUP BY b.book_id, b.title
            HAVING AVG(r.rating) > (SELECT AVG(rating) FROM REVIEW)
        """)
        top_rated = cursor.fetchall()
    conn.close()
    return render_template('reviews.html',
                           all_reviews=all_reviews,
                           top_rated=top_rated)

@app.route('/countries-people')
def countries_people():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT country FROM AUTHOR
            UNION
            SELECT country FROM PUBLISHER
            ORDER BY country
        """)
        all_countries = cursor.fetchall()

        cursor.execute("""
            SELECT country FROM AUTHOR
            INTERSECT
            SELECT country FROM PUBLISHER
        """)
        both_countries = cursor.fetchall()

        cursor.execute("""
            SELECT country FROM AUTHOR
            EXCEPT
            SELECT country FROM PUBLISHER
        """)
        author_only_countries = cursor.fetchall()

        cursor.execute("""
            SELECT name, 'Author' AS type FROM AUTHOR
            UNION ALL
            SELECT name, 'Member' AS type FROM MEMBER
            ORDER BY name
        """)
        people = cursor.fetchall()
    conn.close()
    return render_template('countries_people.html',
                           all_countries=all_countries,
                           both_countries=both_countries,
                           author_only_countries=author_only_countries,
                           people=people)

if __name__ == '__main__':
    app.run(debug=True)