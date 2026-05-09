from app import create_app, db
from app.models import User, Lead, FollowUp, WAMessage

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Lead=Lead, FollowUp=FollowUp)

if __name__ == '__main__':
    app.run(debug=True)
