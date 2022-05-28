#!/usr/bin/python3
import csv
import logging
from enum import Enum
from typing import Tuple

import pandas as pd
import matplotlib.pyplot as plt

# Tour Enum
class TourEnum(Enum):
    ATP = 0
    WTA = 1


# fmt: off
ATP_RESULTS_FILE = "results/atp_top_10_matches.csv"
ATP_SEASON_FILES = [
    # "data/tennis_atp/atp_matches_2019.csv",
    "data/tennis_atp/atp_matches_2020.csv",
    "data/tennis_atp/atp_matches_2021.csv",
    "data/tennis_atp/atp_matches_2022.csv"
]

# ATP BIG TOURNAMENT LOOKUP
ATP_MASTERS_GS_TOURNAMENT_LIST = [
    "Australian Open",
    "Indian Wells Masters", 
    "Miami Masters", 
    "Monte Carlo Masters",
    "Madrid Masters",
    "Rome Masters",
    "Roland Garros",
    "Wimbledon",
    "Canada Masters",
    "Cincinnati Masters",
    "Us Open",
    "Shanghai Masters",
    "Paris Masters"]

# WTA HELPERS
WTA_RESULTS_FILE = "results/wta_top_10_matches.csv"
WTA_SEASON_FILES = [
    # "data/tennis_wta/wta_matches_2019.csv",
    "data/tennis_wta/wta_matches_2020.csv",
    "data/tennis_wta/wta_matches_2021.csv",
    "data/tennis_wta/wta_matches_2022.csv"
]

# WTA BIG TOURNAMENT LOOKUP
WTA_1000_GS_LOOKUP = [
    "Dubai"
    "Doha"
    "Australian Open",
    "Indian Wells", 
    "Miami", 
    "Monte Carlo Masters",
    "Madrid",
    "Rome",
    "Roland Garros",
    "Wimbledon",
    "Montreal",
    "Toronto"
    "Cincinnati",
    "Us Open",
    "Wuhan",
    "Beijing"]

GS_LIST = [
    "Australian Open",
    "Roland Garros",
    "Wimbledon",
    "Us Open"
]

RELEVANT_ROUNDS = ['QF', 'SF', 'F']
LOOKUP_TABLE = {TourEnum.ATP : ATP_MASTERS_GS_TOURNAMENT_LIST, TourEnum.WTA : WTA_1000_GS_LOOKUP}
IMAGE_PREFIX = 'images/'
#HELPER COL IDS
TOURNEY_ID = 1
WINNER_RANK = 45
LOSER_RANK = 47
ROUND = 25

# fmt: on


def parse_top_10_results(
    results_file: str, season_files: list, tour: TourEnum
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Parses the data files, saves to a results file and builds the dataframe

    Args:
        results_file (str) : File to save results.
        season_files (list): List containing filenames containing season data.
        tour (TourEnum): What tour is being processed.

    Returns:
        pd.DataFrame: dataframe containing the top 10 matches.
        pd.DataFrame: dataframe containing all the qf or later matches
    """
    # TODO figure out more pythonic way to build the dataframe as opposed to doing the list first
    top_10_matches = []
    qf_later_matches = []
    header = False
    with open(results_file, "w") as results_file:
        match_writer = csv.writer(results_file)
        for season_file in season_files:
            with open(season_file, "r") as season:
                match_reader = csv.reader(season, delimiter=",")
                for match in match_reader:
                    if header is False:
                        header_val = match
                        match_writer.writerow(header_val)
                        header = True
                    if match[TOURNEY_ID] in LOOKUP_TABLE[tour]:
                        if match[ROUND] in RELEVANT_ROUNDS:
                            top_10_match = 0
                            if match[WINNER_RANK] == "" or match[LOSER_RANK] == "":
                                top_10_match = 0
                            elif (
                                int(match[WINNER_RANK]) <= 10
                                and int(match[LOSER_RANK]) <= 10
                            ):
                                top_10_match = 1
                            new_match = match.copy()
                            new_match.append(top_10_match)
                            qf_later_matches.append(new_match)
                        if match[WINNER_RANK] == "" or match[LOSER_RANK] == "":
                            continue
                        if (
                            int(match[WINNER_RANK]) <= 10
                            and int(match[LOSER_RANK]) <= 10
                        ):
                            logging.debug(f"Qualifed match found: {match}")
                            match_writer.writerow(match)
                            top_10_matches.append(match)
    top_10_matches_df = pd.DataFrame(top_10_matches, columns=header_val)
    header_val.append("top10")
    qf_later_df = pd.DataFrame(qf_later_matches, columns=header_val)
    return top_10_matches_df, qf_later_df


def top_10_match_breakdown(
    tour_dataframe: pd.DataFrame, qf_later: pd.DataFrame, tour: TourEnum
):
    """Generate some plots on top 10 matches

    Args:
        tour_dataframe (pd.DataFrame): Top 10 matches dataframe
        qf_later (pd.DataFrame): Qf or later matches dataframe
        tour (TourEnum): Tour being analyzed

    Returns:
    """

    # TODO if revisiting clean up and break this into subfunctions...
    # Majors vs Masters
    major_mask = tour_dataframe["tourney_name"].isin(GS_LIST)
    major_cnt = len(tour_dataframe[major_mask])
    other_cnt = len(tour_dataframe[~major_mask])
    total_cnt = major_cnt + other_cnt
    tourney_type_df = pd.DataFrame(
        {"type": ["Major", "Non_Major"], "count": [major_cnt, other_cnt]},
        index=["Major", "Non_Major"],
    )

    # Lifted this from here
    # https://stackoverflow.com/questions/59644751/matplotlib-pie-chart-show-both-value-and-percentage
    def val_percent_fmt(x):
        return "{:.4f}%\n({:.0f})".format(x, total_cnt * x / 100)

    tourney_type_df.plot.pie(
        y="count", label="Tournament Type", autopct=val_percent_fmt
    )
    file_name = (
        IMAGE_PREFIX
        + ("ATP" if tour == TourEnum.ATP else "WTA")
        + "_tournament_breakdown.png"
    )
    plt.savefig(file_name)

    # Percentage of Top 10 Matches in QF, SF, Final
    top_ten_mask = qf_later["top10"] == 1
    top10_cnt = len(qf_later[top_ten_mask])
    not_top10_cnt = len(qf_later[~top_ten_mask])
    total_cnt = top10_cnt + not_top10_cnt
    top_10_df = pd.DataFrame(
        {"type": ["Top 10", "Not Top 10"], "count": [top10_cnt, not_top10_cnt]},
        index=["Top 10", "Not Top 10"],
    )

    top_10_df.plot.pie(y="count", label="QF or Later Match", autopct=val_percent_fmt)
    file_name = (
        IMAGE_PREFIX
        + ("ATP" if tour == TourEnum.ATP else "WTA")
        + "_qf_or_later_all.png"
    )
    plt.savefig(file_name)

    # Non Majors QF or later
    major_mask = qf_later["tourney_name"].isin(GS_LIST)
    non_major_df_qf_later = qf_later[~major_mask]
    top_ten_mask = non_major_df_qf_later["top10"] == 1
    top10_cnt = len(non_major_df_qf_later[top_ten_mask])
    not_top10_cnt = len(non_major_df_qf_later[~top_ten_mask])
    total_cnt = top10_cnt + not_top10_cnt
    top_10_df = pd.DataFrame(
        {"type": ["Top 10", "Not Top 10"], "count": [top10_cnt, not_top10_cnt]},
        index=["Top 10", "Not Top 10"],
    )

    top_10_df.plot.pie(y="count", label="QF or Later Match", autopct=val_percent_fmt)
    file_name = (
        IMAGE_PREFIX + "ATP" if tour == TourEnum.ATP else "WTA"
    ) + "_qf_or_later_non_major.png"
    plt.savefig(file_name)

    return


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting analysis")

    atp_top_10_matches, atp_qf_later = parse_top_10_results(
        ATP_RESULTS_FILE, ATP_SEASON_FILES, TourEnum.ATP
    )
    print(atp_qf_later)
    logging.info(f"Total number of top 10 ATP Matches {len(atp_top_10_matches)}")

    top_10_match_breakdown(atp_top_10_matches, atp_qf_later, TourEnum.ATP)

    wta_top_10_matches, wta_qf_later = parse_top_10_results(
        WTA_RESULTS_FILE, WTA_SEASON_FILES, TourEnum.WTA
    )
    logging.info(f"Total number of top 10 WTA Matches {len(wta_top_10_matches)}")

    top_10_match_breakdown(wta_top_10_matches, wta_qf_later, TourEnum.WTA)


if __name__ == "__main__":
    main()
