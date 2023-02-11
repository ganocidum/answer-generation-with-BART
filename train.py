import torch

import os

from src.utils import init_checkpoint_folder, get_gpu_utilization, get_parser, get_logger
from src.trainer import Trainer, prepare_dataset, prepare_training_stuff


def main(args):
    # set seed
    torch.manual_seed(args.seed)
    init_checkpoint_folder(args)

    if args.is_colab and args.logger:
        args.logger = False
        print('Can\'t use logging in notebook')

    if args.logger:
        logger = get_logger(args.is_main, os.path.join(args.checkpoint_path,'run.log'))
    else:
        logger = None

    if (args.logger or args.is_colab) and args.device == 'cuda:0':
        get_gpu_utilization(logger)

    train_dataset = prepare_dataset(logger, args, data_type='train')

    if args.eval_data != None:
        eval_dataset = prepare_dataset(logger, args, data_type="eval")
    else:
        eval_dataset =  None
    
    if (args.logger or args.is_colab) and args.device == 'cuda:0':
        get_gpu_utilization(logger)
    
    tokenizer, model = prepare_training_stuff(logger, args)

    if (args.logger or args.is_colab) and args.device == 'cuda:0':
        get_gpu_utilization(logger)
    
    trainer = Trainer(
            model=model, 
            tokenizer=tokenizer, 
            train_dataset=train_dataset, 
            eval_dataset=eval_dataset, 
            args=args,
            logger=logger)

    if args.logger:
        logger.info('=============Start training=============')
    elif args.is_colab:
        print('=============Start training=============')
    
    trainer.train()

    if (args.logger or args.is_colab) and args.device == 'cuda:0':
        get_gpu_utilization(logger)

    if args.logger:
        logger.info('=============Start predicting on eval_dataset=============')
    elif args.is_colab:
        print('=============Start predicting on eval_dataset=============')
    
    predicted, reference = trainer.predict()

    if args.logger:
        logger.info('=============Start evaluating on eval_dataset=============')
    elif args.is_colab:
        print('=============Start evaluating on eval_dataset=============')

    trainer.evaluate(predicted, reference)


if __name__ == '__main__':
    args = get_parser()
    main(args)