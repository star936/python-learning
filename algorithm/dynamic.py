# coding: utf-8


def dp_make_change(coin_list, change, min_coins, coin_used):
    """
    利用动态规划解决'使用最少的硬币找零'问题
    @Arguments:
        coin_list: 零钱集合，被用于找零
        change: 需要找零的钱数
        min_coins: 存储[0, change+1)之间每个量找零需要的最少硬币数
        coin_used: 记录为min_coins的每一项添加的最后一个硬币
    """
    for cents in range(change+1):
        coin_count = cents
        new_coin = 1
        for j in [c for c in coin_list if c <= cents]:
            # min_coins[cents-j]表示(cents-j)钱数需要的最少找零数
            if min_coins[cents-j] + 1 < coin_count:
                coin_count = min_coins[cents-j] + 1
                new_coin = j
        min_coins[cents] = coin_count
        coin_used[cents] = new_coin
    return min_coins[change]


def print_coins(coin_used, change):
    coin = change
    while coin > 0:
        this_coin = coin_used[coin]
        print(this_coin)
        coin = coin - this_coin


def main():
    amnt = 63
    clist = [1, 5, 10, 21, 25]
    coin_used = [0] * (amnt+1)
    coin_count = [0] * (amnt+1)
    dp_make_change(clist, amnt, coin_count, coin_used)
    print_coins(coin_used, amnt)
