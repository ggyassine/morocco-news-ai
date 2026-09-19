from db import conn
from classifier import classify


def reprocess_all_news():

    updated = 0

    with conn() as c:

        rows = c.execute(
            """
            SELECT *
            FROM news
            ORDER BY id ASC
            """
        ).fetchall()

        print(
            f"Found {len(rows)} news items"
        )

        for row in rows:

            item = dict(row)

            try:
                result = classify(item)

                c.execute(
                    """
                    UPDATE news
                    SET
                        trust = ?,
                        category = ?,
                        status = ?,
                        summary = ?,
                        player = ?
                    WHERE id = ?
                    """,
                    (
                        result.get(
                            "trust",
                            item.get("trust", "C")
                        ),

                        result.get(
                            "category",
                            item.get("category")
                        ),

                        result.get(
                            "status",
                            item.get("status")
                        ),

                        result.get(
                            "summary",
                            item.get("summary")
                        ),

                        result.get(
                            "player",
                            item.get("player", "")
                        ),

                        item["id"],
                    )
                )

                updated += 1

            except Exception as e:

                print(
                    f"Error processing "
                    f"news {item.get('id')}: {e}"
                )

        c.commit()

    print(
        f"Reprocessed {updated} news items"
    )


if __name__ == "__main__":

    reprocess_all_news()
