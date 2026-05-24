# TaskHub CLI 📝

**TaskHub CLI** — це сучасний, гнучкий консольний застосунок для керування завданнями, розроблений мовою Python 3.12+ із дотриманням передових стандартів архітектури та інженерного проектування (SOLID, GRASP, KISS, DRY, YAGNI).

---

## 🚀 Документація користувача (CLI User Guide)

Застосунок запускається з кореневої директорії проекту за допомогою інтерпретатора Python як модуль:
```bash
python3 -m intpy [команда] [аргументи]
```

### Доступні команди та їх функціонал

#### 1. Додавання завдання (`add`)
Створює нове завдання зі статусом `TODO`.
- **Аргументи**:
  - `title` (обов'язковий, позиційний) — назва завдання.
  - `-d`, `--desc` / `--description` (опціональний) — детальний опис.
  - `-p`, `--priority` (опціональний) — пріоритет (`LOW`, `MEDIUM`, `HIGH`). За замовчуванням: `MEDIUM`.
- **Приклад**:
  ```bash
  python3 -m intpy add "Підготувати звіт" --desc "Написати висновки до лабораторної роботи №1" --priority HIGH
  ```

#### 2. Перегляд списку завдань (`show`)
Виводить список завдань у вигляді структурованої таблиці з рамками Unicode та кольоровим підсвічуванням статусів і пріоритетів.
- **Аргументи**:
  - `-s`, `--status` (опціональний) — фільтрувати за статусом (`TODO`, `IN_PROGRESS`, `DONE`).
  - `-p`, `--priority` (опціональний) — фільтрувати за пріоритетом (`LOW`, `MEDIUM`, `HIGH`).
  - `--sort` (опціональний) — сортувати список (`id`, `priority`, `status`, `created`, `updated`). За замовчуванням: `id`.
- **Приклади**:
  ```bash
  # Показати всі завдання
  python3 -m intpy show
  
  # Показати тільки завдання в процесі виконання, відсортовані за пріоритетом
  python3 -m intpy show --status IN_PROGRESS --sort priority
  ```

#### 3. Редагування завдання (`edit`)
Дозволяє оновити будь-які атрибути вже існуючого завдання.
- **Аргументи**:
  - `id` (обов'язковий, позиційний) — числовий ідентифікатор завдання.
  - `-t`, `--title` (опціональний) — нова назва завдання.
  - `-d`, `--desc` (опціональний) — новий опис.
  - `-s`, `--status` (опціональний) — новий статус.
  - `-p`, `--priority` (опціональний) — новий пріоритет.
- **Приклад**:
  ```bash
  python3 -m intpy edit 1 --title "Підготувати фінальний звіт" --priority MEDIUM
  ```

#### 4. Швидкий запуск виконання (`start`)
Переводить завдання в статус виконання (`IN_PROGRESS`). Shortcut для `edit ID --status IN_PROGRESS`.
- **Аргументи**:
  - `id` (обов'язковий, позиційний) — ідентифікатор завдання.
- **Приклад**:
  ```bash
  python3 -m intpy start 1
  ```

#### 5. Швидке завершення завдання (`complete`)
Позначає завдання як виконане (`DONE`). Shortcut для `edit ID --status DONE`.
- **Аргументи**:
  - `id` (обов'язковий, позиційний) — ідентифікатор завдання.
- **Приклад**:
  ```bash
  python3 -m intpy complete 1
  ```

#### 6. Видалення завдання (`delete`)
Видаляє завдання з бази даних безповоротно.
- **Аргументи**:
  - `id` (обов'язковий, позиційний) — ідентифікатор завдання.
- **Приклад**:
  ```bash
  python3 -m intpy delete 1
  ```

#### 7. Конфігурація бази даних (`--db`)
За замовчуванням дані зберігаються у файлі `tasks.json` у поточній робочій директорії. За допомогою глобального прапорця `--db` можна вказати альтернативний шлях.
- **Приклад**:
  ```bash
  python3 -m intpy --db custom_db.json show
  ```

---

## 🏗️ Технічна реалізація (Technical Architecture)

Проект побудовано за концепцією **Багатошарової архітектури (Layered Architecture)**, що забезпечує чітке розділення відповідальностей (Separation of Concerns).

```
intpy/
│
├── domain/                  # Шара бізнес-сутностей (Domain Layer)
│   ├── exceptions.py        # Специфічні для домену помилки
│   └── models.py            # Сутність Task, Enums та бізнес-правила
│
├── repository/              # Шара збереження даних (Data Access Layer)
│   ├── interface.py         # Абстрактний інтерфейс сховища
│   └── json_repo.py         # JSON-реалізація інтерфейсу з атомарним записом
│
├── service/                 # Шара бізнес-сценаріїв (Use Cases / Service Layer)
│   └── task_service.py      # Оркестрація операцій та додаткова валідація
│
├── presentation/            # Шара представлення (Presentation Layer)
│   ├── cli.py               # Консольний інтерфейс та парсинг argparse
│   └── formatter.py         # Форматування ANSI/Unicode таблиць та карток
│
├── main.py                  # Вхідна точка CLI додатка
└── __main__.py              # Точка запуску як модуля Python
```

### Застосовані паттерни та принципи

- **Single Responsibility Principle (SRP)**: Кожен файл відповідає лише за один аспект системи. Наприклад, `cli.py` відповідає виключно за введення/виведення та парсинг параметрів, а `models.py` — за внутрішні правила валідації сутності.
- **Open/Closed Principle (OCP) & Dependency Inversion Principle (DIP)**: Сервіс `TaskService` не знає деталей роботи з диском. Він приймає через конструктор інтерфейс `TaskRepository`. Якщо ви захочете перейти на SQLite або PostgreSQL, достатньо написати нову реалізацію репозиторію, не змінюючи бізнес-логіку та CLI.
- **KISS, DRY & YAGNI**: Жодних зайвих залежностей. Використано чистий стандартний функціонал Python 3.12 (такий як `@dataclass(slots=True)` для оптимізації пам'яті, конструкція `match/case` для диспетчеризації команд та `pathlib` для роботи зі шляхами).
- **Атомарний запис файлів (Atomic File Writes)**:
  Щоб захистити базу даних від пошкодження під час аварійного вимкнення програми, `JsonTaskRepository` спочатку записує дані у тимчасовий файл `tasks.json.tmp`, а потім виконує атомарну заміну оригінального файлу.

---

## 🛠️ Як розробляти та додавати нові фічі (Developer's Guide)

Оскільки система слабозв'язана, процес додавання нового функціоналу є структурованим і передбачуваним. Розглянемо два найпопулярніших сценарії.

### Сценарій А: Додавання нової властивості до завдання (наприклад, "Category" / Категорія)

1. **Крок 1 (Domain Layer)**:
   Відкрийте [domain/models.py](file:///home/mykola/PycharmProjects/211_lib_py/intpy/domain/models.py):
   - Додайте поле до класу `Task`: `category: str = ""` (і не забудьте оновити `slots` або виклик конструктора).
   - Оновіть методи серіалізації `to_dict` та `from_dict` для підтримки нового поля.
   - Додайте бізнес-правила валідації у метод `validate` (наприклад, довжина категорії не більше 20 символів).
2. **Крок 2 (Service Layer)**:
   Відкрийте [service/task_service.py](file:///home/mykola/PycharmProjects/211_lib_py/intpy/service/task_service.py):
   - Оновіть метод `create_task` та `update_task`, щоб вони приймали аргумент `category: str | None = None`.
3. **Крок 3 (Presentation Layer)**:
   - Відкрийте [presentation/formatter.py](file:///home/mykola/PycharmProjects/211_lib_py/intpy/presentation/formatter.py) та додайте колонку `"Category"` у `format_task_table` та виведіть її в `format_single_task`.
   - Відкрийте [presentation/cli.py](file:///home/mykola/PycharmProjects/211_lib_py/intpy/presentation/cli.py) та додайте прапорець `-c` / `--category` у парсери команд `add` та `edit`, після чого передайте отримане значення в сервіс.

---

### Сценарій Б: Додавання нової CLI-команди (наприклад, "clear" — очистити всі завдання)

1. **Крок 1 (Repository Layer)**:
   Відкрийте [repository/interface.py](file:///home/mykola/PycharmProjects/211_lib_py/intpy/repository/interface.py):
   - Оголосіть новий абстрактний метод:
     ```python
     @abstractmethod
     def delete_all(self) -> None:
         """Delete all tasks from repository."""
         pass
     ```
   - Реалізуйте цей метод у [repository/json_repo.py](file:///home/mykola/PycharmProjects/211_lib_py/intpy/repository/json_repo.py):
     ```python
     def delete_all(self) -> None:
         self._save_raw({"tasks": [], "next_id": 1})
     ```
2. **Крок 2 (Service Layer)**:
   Відкрийте [service/task_service.py](file:///home/mykola/PycharmProjects/211_lib_py/intpy/service/task_service.py):
   - Додайте метод сервісу:
     ```python
     def clear_hub(self) -> None:
         """Deletes all tasks completely."""
         self.repository.delete_all()
     ```
3. **Крок 3 (Presentation Layer)**:
   Відкрийте [presentation/cli.py](file:///home/mykola/PycharmProjects/211_lib_py/intpy/presentation/cli.py):
   - Додайте новий субпарсер для команди `clear`:
     ```python
     clear_parser = subparsers.add_parser("clear", help="Remove all tasks from TaskHub.")
     ```
   - Додайте кейс у блок `match parsed_args.command`:
     ```python
     case "clear":
         service.clear_hub()
         print("\033[92m✔ All tasks cleared successfully!\033[0m")
     ```

Завдяки такій структурі код залишається чистим, легко тестується юніт-тестами та виключає появу непередбачуваних багів у суміжних модулях!
