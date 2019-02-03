import sys

STANDARD_LEN = 6


def get_stick_diffs(cur_state, pre_state):
    cur_produced_sticks = cur_state['produced_sticks']
    pre_produced_sticks = pre_state['produced_sticks']
    # print("cur_produced_sticks: {}".format(cur_produced_sticks))
    # print("pre_produced_sticks: {}".format(pre_produced_sticks))
    stick_diffs = {}
    for cur_stick_len, cur_amount in cur_produced_sticks.items():
        # print("cur_stick_len: {}, cur_amount: {}".format(cur_stick_len, cur_amount))
        if cur_stick_len not in pre_produced_sticks:
            raise ValueError("stick_len {} not exists".format(cur_stick_len))
        elif pre_produced_sticks[cur_stick_len] <= cur_amount:
            diff = cur_amount - pre_produced_sticks[cur_stick_len]
            # print("cal diff: {}".format(diff))
            stick_diffs[cur_stick_len] = diff
        else:
            raise ValueError("stick_len {} "
                             "diff is negative".format(cur_stick_len))
    return stick_diffs

# def is_pre_state(cur_state, pre_state):
#     cur_produced_sticks = cur_state['produced_sticks']
#     pre_produced_sticks = pre_state['produced_sticks']
#     diff = 0
#     for cur_stick_len, cur_amount in cur_produced_sticks.items():
#
#         if cur_stick_len not in pre_produced_sticks:
#             return False
#         elif pre_produced_sticks[cur_stick_len] < cur_amount:
#             diff = diff + cur_amount - pre_produced_sticks[cur_stick_len]
#         else:
#             pre_amount = pre_produced_sticks[cur_stick_len]
#             raise ValueError('pre_produced_stick amount {pre_amount} should not'
#                              ' be greater than cur_produced_stick amount: '
#                              '{cur_amount}'.format(
#                 pre_amount=pre_amount, cur_amount=cur_amount))
#     if diff == 1:
#         return True
#     else:
#         return False

def init_state():
    # may be assign amount infinite
    raise NotImplementedError('TODO')


def has_remained_stick(remained_stick_lens, remained_stick_len):
    if remained_stick_len not in remained_stick_lens:
        raise ValueError("remained_stick_len not in remained_stick_lens")
    if remained_stick_lens[remained_stick_len] > 0:
        return True
    else:
        return False


def update_remained_sticks(remained_sticks, remained_stick_len, stick_len, is_cut=True):
    # cut remained stick, not standard stick
    if is_cut is True:
        remained_sticks[remained_stick_len] = remained_sticks[remained_stick_len] - 1

    new_remained_stick_len = remained_stick_len - stick_len
    if new_remained_stick_len > 0:
        if new_remained_stick_len not in remained_sticks:
            remained_sticks[new_remained_stick_len] = 1
        else:
            amount = remained_sticks[new_remained_stick_len]
            amount = amount + 1
            remained_sticks[new_remained_stick_len] = amount
    return remained_sticks


def cut_remained_sticks(remained_sticks, stick_len):
    is_cut = False
    print("remained_sticks: {}".format(remained_sticks))
    for remained_stick_len, amount in remained_sticks.items():
        if ((remained_stick_len >= stick_len) and
            (has_remained_stick(remained_sticks, remained_stick_len))):
            remained_sticks = update_remained_sticks(
                remained_sticks, remained_stick_len, stick_len)
            is_cut = True
            return is_cut, remained_sticks
    return is_cut, remained_sticks


def produce_sticks(remained_sticks: dict, stick_len, diff):
    amount_delta = 0
    for i in range(1, diff + 1):
        is_cut, remained_stick_lens = cut_remained_sticks(remained_sticks, stick_len)
        if is_cut is False:
            # is_cut is False, remained_stick not fit, need use new stick
            amount_delta = amount_delta + 1
            remained_sticks = update_remained_sticks(
                remained_sticks=remained_sticks,
                remained_stick_len=STANDARD_LEN,
                stick_len=stick_len,
                is_cut=is_cut
            )
    return remained_sticks, amount_delta


def cal_amount(cur_state, pre_state):
    pre_remained_sticks = pre_state['remained_sticks']
    pre_produced_sticks = pre_state['produced_sticks']
    print("pre_remained_sticks: {}".format(pre_remained_sticks))
    print("pre_produced_sticks: {}".format(pre_produced_sticks))
    stick_diffs = get_stick_diffs(cur_state, pre_state)
    print("stick_diffs: {}".format(stick_diffs))
    amount = pre_state['amount']
    remained_sticks = None
    for stick_len, diff in stick_diffs.items():
        if diff > 0:
            print("try to produce stick, sitck_len: {}, diff: {}".format(stick_len, diff))
            remained_sticks, amount_delta = produce_sticks(
                pre_remained_sticks, stick_len, diff)
            print("current_state: {}".format(cur_state))
            print("pre_state: {}".format(pre_state))
            print("remained_sticks: {}, amount_delta: {}".format(remained_sticks, amount_delta))
            amount = amount + amount_delta
    return remained_sticks, amount


def traverse_states(states: list, current_state, stick_len):
    # TODO: handle empty states?
    if len(states) == 0:
        remained_stick_len = STANDARD_LEN - stick_len
        remained_sticks = {
            remained_stick_len: 1
        }
        current_state['remained_sticks'] = remained_sticks
        current_state['amount'] = 1
        return current_state
    min_amount = sys.maxsize
    state_idx = -1
    for state in states:
        # try to calculate amount
        state_idx = state_idx + 1
        remained_sticks, amount = cal_amount(current_state, state)
        if amount < min_amount:
            min_amount = amount
            current_state['remained_sticks'] = remained_sticks
            current_state['pre_state'] = state_idx
            current_state['amount'] = min_amount
            print("update min state: {}".format(current_state))
        else:
            continue
    return current_state


# state = {"produced_sticks": {}, "remained_sticks": {}, amount: }
def botup(needs: dict):
    stick_lens = list(needs.keys())
    # initialize
    produced_sticks = {stick_len: 0 for (stick_len, need) in needs.items()}
    print("produced_sticks: {}".format(produced_sticks))
    states = []
    for stick_len in stick_lens:
        print("try stick_len: {}".format(stick_len))
        if produced_sticks[stick_len] == needs[stick_len]:
            print("hit, continue")
            continue
        else:
            for i in range(1, needs[stick_len] + 1):
                # init current state
                produced_sticks[stick_len] = produced_sticks[stick_len] + 1
                remained_sticks = {}
                current_state = {
                    'produced_sticks': produced_sticks.copy(),
                    'remained_sticks': remained_sticks,
                    'pre_state': -1,
                    'amount': sys.maxsize
                }
                # traverse states
                print("before traverse state: {}".format(current_state))
                print("before states: {}".format(states))
                current_state = traverse_states(states, current_state, stick_len)
                states.append(current_state)
                print("after states: {}".format(states))
                print("after traverse state: {}".format(current_state))

needs = {5: 3, 4: 3, 3: 3, 0.5: 2, 0.3: 4}
botup(needs)
