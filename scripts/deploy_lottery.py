from brownie import Lottery, config, network
from scripts.helper import get_account, get_contract, fund_with_link
import time

def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(get_contract("eth_usd_price_feed").address,
                             get_contract("vrf_coordinator").address,
                             get_contract("link_token").address,
                             config["networks"][network.show_active()]["fee"],
                             config["networks"][network.show_active()]["keyhash"],
                             {"from": account},
                             publish_source= config["networks"][network.show_active()].get("verify"))
    return lottery

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("lottery started")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("entered the lottery")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    fund_with_link(lottery.address)
    tx = lottery.endLottery({"from": account})
    tx.wait(1)
    time.sleep(180)
    print(f"the winner is {lottery.recentWinner()}")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()