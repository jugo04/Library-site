# 📚 Library Site

A full-featured online library service built with Django REST Framework. Users can browse books, read them online, leave reviews, rate books, manage their reading list, and subscribe to premium plans.

---

## 🚀 Features

- 📖 Browse books with filtering by genre, series, and author
- 🔍 Full-text search with trigram similarity (books, authors, series)
- ⭐ Book rating system with weighted average ranking
- 💬 Book reviews (one per user per book)
- ❤️ Favorite and reading list management
- 👤 User profiles with public and private views
- 🏆 Achievement system
- 📚 Book series support
- 💳 Subscription plans (Basic, Family)
- 👨‍👩‍👧‍👦 Family group with invite system
- 🛒 Individual book purchases (without subscription)
- 🔐 Token-based authentication via Djoser
- 📄 Pagination support

---

## 🛠 Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** Djoser + Token Auth
- **Search:** PostgreSQL Trigram Similarity (`pg_trgm`)
- **Filtering:** django-filter

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/jugo04/Library-site.git
cd Library-site
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```
SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Enable PostgreSQL trigram extension
```sql
CREATE EXTENSION pg_trgm;
```

### 6. Apply migrations
```bash
python manage.py migrate
```

### 7. Create superuser
```bash
python manage.py createsuperuser
```

### 8. Run the server
```bash
python manage.py runserver
```

---

## 📡 API Endpoints

### 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/users/` | Register |
| POST | `/auth/token/login/` | Login (get token) |
| POST | `/auth/token/logout/` | Logout |

### 📚 Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/library/` | List all books |
| GET | `/api/library/{id}/` | Book details |
| POST | `/api/library/{id}/interact/` | Like, read, rate a book |
| GET | `/api/library/{id}/reviews/` | Get book reviews |
| POST | `/api/library/{id}/reviews/` | Add a review |

### 👥 Authors
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/authors/` | List all authors |
| GET | `/api/authors/{id}/` | Author details with books |

### 📖 Series
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/series/` | List all series |
| GET | `/api/series/{id}/` | Series details with books |

### 🎭 Genres
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/genres/` | List all genres |

### 🔍 Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search/?q={query}&type={type}` | Search books, authors, series |

### 👤 Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/{id}/` | Public profile |
| GET | `/api/profile/settings/` | Own profile settings |
| PATCH | `/api/profile/settings/` | Update profile |

### 💳 Subscriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/plans/` | List subscription plans |

### ❤️ Personal Lists
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/favorite/` | Favorite books |
| GET | `/api/readed/` | Read books |

---

## 📂 Project Structure

```
Library-site/
├── WebLibrary/          # Project settings
│   ├── settings.py
│   └── urls.py
├── books/               # Main app
│   ├── models.py        # All models
│   ├── views.py         # ViewSets and API views
│   ├── serializer.py    # Serializers
│   ├── signals.py       # Signals (file deletion, achievements)
│   └── migrations/
├── manage.py
└── requirements.txt
```

---

## 🗄 Main Models

- `User` — custom user model extending AbstractUser
- `Book` — book with cover, PDF, genre, author, series, age category
- `Author` — author with biography and photo
- `Genre` — book genre
- `Series` — book series
- `BookStatus` — user interaction with a book (favorite, read, rating)
- `Review` — user review for a book
- `Achievement` / `UserAchievement` — achievement system
- `SubscriptionPlan` / `UserSubscription` — subscription management
- `BookPurchase` — individual book purchase
- `FamilyGroup` / `FamilyInvite` — family subscription management

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
