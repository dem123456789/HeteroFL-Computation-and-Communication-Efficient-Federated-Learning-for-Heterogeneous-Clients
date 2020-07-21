import argparse
import itertools

parser = argparse.ArgumentParser(description='Config')
parser.add_argument('--run', default='train', type=str)
parser.add_argument('--file', default='classifier', type=str)
parser.add_argument('--model', default=None, type=str)
parser.add_argument('--fed', default=1, type=int)
parser.add_argument('--num_gpu', default=4, type=int)
parser.add_argument('--world_size', default=1, type=int)
parser.add_argument('--round', default=4, type=int)
parser.add_argument('--experiment_step', default=1, type=int)
parser.add_argument('--num_experiments', default=1, type=int)
parser.add_argument('--num_epochs', default=200, type=int)
parser.add_argument('--resume_mode', default=0, type=int)
args = vars(parser.parse_args())


def main():
    run = args['run']
    file = args['file']
    model = args['model']
    fed = args['fed']
    num_gpu = args['num_gpu']
    world_size = args['world_size']
    round = args['round']
    experiment_step = args['experiment_step']
    num_experiments = args['num_experiments']
    gpu_ids = [','.join(str(i) for i in list(range(x, x + world_size))) for x in list(range(0, num_gpu, world_size))]
    filename = '{}_{}'.format(run, file)
    if fed:
        script_name = [['{}_{}_fed.py'.format(run, file)]]
    else:
        script_name = [['{}_{}.py'.format(run, file)]]
    data_names = [['MNIST', 'CIFAR10']]
    model_names = [[model]]
    init_seeds = [list(range(0, num_experiments, experiment_step))]
    world_size = [[world_size]]
    num_experiments = [[experiment_step]]
    if fed:
        control_name = [['SGD'], ['iid'], ['100'], ['0.1'], ['0.5']]
    else:
        control_name = [['SGD'], ['none']]
    print(control_name)
    control_names = [['_'.join(x) for x in itertools.product(*control_name)]]
    controls = script_name + data_names + model_names + init_seeds + world_size + num_experiments + \
               control_names
    controls = list(itertools.product(*controls))
    s = '#!/bin/bash\n'
    k = 0
    for i in range(len(controls)):
        controls[i] = list(controls[i])
        s = s + 'CUDA_VISIBLE_DEVICES=\"{}\" python {} --data_name {} --model_name {} --init_seed {} ' \
                '--world_size {} --num_experiments {} --resume_mode {} --control_name {}&\n'.format(
            gpu_ids[k % len(gpu_ids)], *controls[i])
        if k % round == round - 1:
            s = s[:-2] + '\n'
        k = k + 1
    print(s)
    run_file = open('./{}.sh'.format(filename), 'w')
    run_file.write(s)
    run_file.close()
    return


if __name__ == '__main__':
    main()