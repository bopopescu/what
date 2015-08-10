"""adds stored_at column in twitter_tweet_samples and twitter_tweets schemas

Revision ID: 12c41f6f39a
Revises: 442de3177362
Create Date: 2015-03-31 18:33:55.114062

"""

# revision identifiers, used by Alembic.
revision = '12c41f6f39a'
down_revision = '442de3177362'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('twitter_tweet_samples', sa.Column('stored_at', sa.TIMESTAMP(), server_default=sa.text(u'CURRENT_TIMESTAMP'), nullable=True))
    #op.create_index('stored_at_idx', 'twitter_tweet_samples', ['stored_at'], unique=False)
    #op.add_column('twitter_tweets', sa.Column('stored_at', sa.TIMESTAMP(), server_default=sa.text(u'CURRENT_TIMESTAMP'), nullable=True))
    #op.create_index('stored_at_idx', 'twitter_tweets', ['stored_at'], unique=False)
    ### end Alembic commands ###

    # NOTE: Since alembic presently doesn't support multiple
    # alter_specifications per ALTER TABLE statement, it could take some hours
    # to execute the following logic in individual ALTER TABLE statements on the
    # 12+ million row tables. So, we construct SQL by hand to work around this.

    # While adding the stored_at column, we wish it to have NULL in the
    # pre-existing rows, since we really don't know when they were inserted. To
    # accomplish this, we define the column with DEFAULT NULL in the first
    # operation and then MODIFY it with DEFAULT CURRENT_TIMESTAMP in the second.
    # Combining both those operations into one was resulted in "unknown column"
    # error from MySQL.
    op.execute(
        "ALTER TABLE `twitter_tweet_samples` "
        "  ADD COLUMN `stored_at` TIMESTAMP NULL DEFAULT NULL"
    )

    op.execute(
        "ALTER TABLE `twitter_tweet_samples` "
        "  MODIFY COLUMN `stored_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
        "  ADD INDEX `stored_at_idx` (`stored_at`)"
    )


    op.execute(
        "ALTER TABLE `twitter_tweets` "
        "  ADD COLUMN `stored_at` TIMESTAMP NULL DEFAULT NULL"
    )

    op.execute(
        "ALTER TABLE `twitter_tweets` "
        "  MODIFY COLUMN `stored_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
        "  ADD INDEX `stored_at_idx` (`stored_at`)"
    )



def downgrade():
    raise NotImplementedError("Rollback is not supported.")
