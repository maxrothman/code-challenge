#!/usr/bin/env python

import os
import click
import db, lib

@click.group()
def main(): pass


@main.command()
@click.option('-d', '--make-dummy-data', is_flag=True)
@click.option('-c', '--clean', is_flag=True)
def init_db(make_dummy_data, clean):
    if clean:
        os.remove(db.DATABASE_FNAME)

    db.Base.metadata.create_all(db.get_engine())

    if make_dummy_data:
        with db.in_session() as s:
            lib.make_dummy_data(s)


@main.command()
@click.argument('question_id', type=int)
@click.option('-e', '--version', type=int)
@click.pass_context
def diff_question(ctx, question_id, version):
    with db.in_session() as s:
        try:
            click.echo('\n'.join(lib.gen_diff(s, question_id, version)))
        except lib.AppError as e:
            ctx.fail(e.message)


@main.command()
@click.argument('question_id', type=int)
@click.argument('text')
@click.pass_context
def update_question_text(ctx, question_id, text):
    with db.in_session() as s:
        try:
            lib.update_question_text(s, question_id, text)
        except lib.AppError as e:
            ctx.fail(e.message)


if __name__ == '__main__':
    main()
