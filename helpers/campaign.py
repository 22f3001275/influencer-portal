import re
import pyotp


def generate_completion_codes(goals):
    goals_list = re.split(';', goals)
    total_weights = 0
    for goal in goals_list:
        total_weights += int(re.split('=', goal)[1])
    print(total_weights)
    weight_for_100 = int(100/total_weights)
    no_of_checkpoints = len(goals_list)
    checkpoint_weights = [int(re.split('=', goal)[1])
                          * weight_for_100 for goal in goals_list]
    spare = 100 - sum(checkpoint_weights)

    secret_keys = [pyotp.TOTP(pyotp.random_base32()).now()
                   for i in range(no_of_checkpoints + 1)]
    return {'completion_keys': ';'.join(key for key in secret_keys),
            'no_of_checkpoints': no_of_checkpoints,
            'checkpoint_weight': ';'.join(str(weight) for weight in checkpoint_weights),
            'spare': spare
            }


def checkpoints(goals, secret_key, checkpoint_weight, spare):
    checkpoint_weight = re.split(';', checkpoint_weight)
    no_of_checkpoints = len(checkpoint_weight)
    goals_list = re.split(';', goals)
    keys = re.split(';', secret_key)

    checkpoints = [[re.split('=', goal)[0]] for goal in goals_list]
    for i in range(no_of_checkpoints):
        checkpoints[i].extend([checkpoint_weight[i], keys[i]])
    checkpoints.append(['Finish', spare, keys[no_of_checkpoints]])

    return checkpoints
