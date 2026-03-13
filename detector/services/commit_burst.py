from datetime import timedelta


def detect_commit_burst(commits):

    timestamps = [c.commit.author.date for c in commits]

    bursts = 0

    for i in range(1, len(timestamps)):

        delta = timestamps[i] - timestamps[i-1]

        if delta < timedelta(minutes=2):
            bursts += 1

    return bursts