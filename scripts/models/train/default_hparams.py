DEFAULT_HPARAMS = {
    'model': 'multichain',
    'matches': 'transformer',  #
    'term_hidden_dim': 32,  #
    'energies_hidden_dim': 32,  #
    'gradient_checkpointing': True,  #
    'cov_features': 'all_raw',  #
    'cov_compress': 'ffn',  #
    'num_pair_stats': 28,  #
    'num_sing_stats': 0,  #
    'resnet_blocks': 4,  #
    'term_layers': 4,  #
    'term_heads': 4,  #
    'conv_filter': 3,  #
    'matches_layers': 4,  #
    'matches_num_heads': 4,  #
    'k_neighbors': 30,  #
    'contact_idx': True,  #
    'fe_dropout': 0.1,  #
    'fe_max_len': 1000,  #
    'transformer_dropout': 0.1,  #
    'term_use_mpnn': True,  #
    'energies_protein_features': 'full',  #
    'energies_augment_eps': 0,  #
    'energies_encoder_layers': 6,  #
    'energies_dropout': 0.1,  #
    'energies_use_mpnn': False,  #
    'energies_output_dim': 20 * 20,  #
    'energies_gvp': False,  #
    'energies_full_graph': True,  #
    'res_embed_linear': False,  #
    'matches_linear': False,  #
    'term_mpnn_linear': False,  #
    'struct2seq_linear': False,
    'use_terms': True,  #
    'term_matches_cutoff': None,
    # 'test_term_matches_cutoff': None,
    # ^ is an optional hparam if you want to use a different TERM matches cutoff during validation/testing vs training
    'use_coords': True,
    'train_batch_size': 16,
    'shuffle': True,
    'sort_data': True,
    'semi_shuffle': False,
    'regularization': 0,
    'max_term_res': 55000,
    'max_seq_tokens': 0,
    'term_dropout': False,
    'num_features':
        len(['sin_phi', 'sin_psi', 'sin_omega',
             'cos_phi', 'cos_psi', 'cos_omega',
             'env',
             'rmsd',
             'term_len'])  #
}
